# -*- coding: utf-8 -*-

"""
<ENTER DESCRIPTION HERE>
"""
import cv2
import torch
from k_util.logger import Logger
from torch import optim
from torchvision import models
import numpy as np
from torchvision.transforms import transforms

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class TransferNet:
    K_TORCH_GPU = "cuda"
    K_TORCH_CPU = "cpu"
    K_IMAGE_SIZE: int = 400

    def __init__(self):

        # Get the pre-trained VGG19 Model.
        self.vgg = models.vgg19(pretrained=True).features

        # Freeze all layers. We don't need to train this.
        for param in self.vgg.parameters():
            param.requires_grad_(False)

        # Move the device to GPU if available.
        self.device = torch.device(self.K_TORCH_GPU if torch.cuda.is_available() else self.K_TORCH_CPU)
        self.vgg.to(self.device)

        self.tensor_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406),
                                 (0.229, 0.224, 0.225))
        ])

        # weights for each style layer
        # weighting earlier layers more will result in *larger* style artifacts
        # notice we are excluding `conv4_2` our content representation
        self.style_weights = {'conv1_1': 1.,
                              'conv2_1': 0.75,
                              'conv3_1': 0.2,
                              'conv4_1': 0.2,
                              'conv5_1': 0.2}

        self.content_weight = 1  # alpha
        self.style_weight = 1e6  # beta

        Logger.field("Torch Device", self.device)

    def convert_image(self, image: np.ndarray):
        """ Converts a CV2/Numpy image into PyTorch format. """
        image_tensor = self.tensor_transform(image)
        image_tensor = image_tensor.unsqueeze(0)
        image_tensor = image_tensor.to(self.device)
        return image_tensor

    def load_image(self, image_path: str, gray: bool=False):
        """ Load an image from disk. """
        image = cv2.imread(image_path)
        image = cv2.resize(image, (self.K_IMAGE_SIZE, self.K_IMAGE_SIZE))
        if gray:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return self.convert_image(image)

    def convert_tensor_to_image(self, tensor):
        """ Display a tensor as an image. """

        image = tensor.to(self.K_TORCH_CPU).clone().detach()
        image = image.numpy().squeeze()
        image = image.transpose(1, 2, 0)
        image = image * np.array((0.229, 0.224, 0.225)) + np.array((0.485, 0.456, 0.406))
        image = image.clip(0, 1)
        image *= 255
        image = image.astype(np.uint8)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        return image

    def process(self, content_image_path: str, style_image_path: str):
        Logger.field("Processing Content", content_image_path)
        Logger.field("Processing Style", style_image_path)
        content_tensor = self.load_image(content_image_path)
        style_tensor = self.load_image(style_image_path)

        content_features = self.get_features(content_tensor, self.vgg)
        style_features = self.get_features(style_tensor, self.vgg)
        style_grams = {layer: self.gram_matrix(style_features[layer]) for layer in style_features}

        gray_content = self.load_image("../input/octopus.jpg", gray=True)
        g_image = np.zeros((self.K_IMAGE_SIZE, self.K_IMAGE_SIZE, 3), dtype=np.uint8)
        gray_content = self.convert_image(g_image)
        target_tensor = gray_content.clone().requires_grad_(True).to(self.device)

        # for displaying the target image, intermittently
        show_every = 250
        optimizer = optim.Adam([target_tensor], lr=0.003)
        steps = 3000

        for ii in range(1, steps + 1):

            # get the features from your target image
            target_features = self.get_features(target_tensor, self.vgg)

            # the content loss
            content_loss = torch.mean((target_features['conv4_2'] - content_features['conv4_2']) ** 2)

            # the style loss
            # initialize the style loss to 0
            style_loss = 0
            # then add to it for each layer's gram matrix loss
            for layer in self.style_weights:
                # get the "target" style representation for the layer
                target_feature = target_features[layer]
                target_gram = self.gram_matrix(target_feature)
                _, d, h, w = target_feature.shape
                # get the "style" style representation
                style_gram = style_grams[layer]
                # the style loss for one layer, weighted appropriately
                layer_style_loss = self.style_weights[layer] * torch.mean((target_gram - style_gram) ** 2)
                # add to the style loss
                style_loss += layer_style_loss / (d * h * w)

            # calculate the *total* loss
            total_loss = self.content_weight * content_loss + self.style_weight * style_loss

            # update your target image
            optimizer.zero_grad()
            total_loss.backward()
            optimizer.step()

            # display intermediate images and print the loss
            if ii % show_every == 0:
                out_image = self.convert_tensor_to_image(target_tensor)
                cv2.imwrite(f"out_{ii}.png", out_image)
                print('Total loss: ', total_loss.item())

    def get_features(self, image, model, layers=None):
        """ Run an image forward through a model and get the features for
            a set of layers. Default layers are for VGGNet matching Gatys et al (2016)
        """

        if layers is None:
            layers = {'0': 'conv1_1',
                      '5': 'conv2_1',
                      '10': 'conv3_1',
                      '19': 'conv4_1',
                      '21': 'conv4_2',
                      '28': 'conv5_1'}

        features = {}
        x = image

        for name, layer in model._modules.items():
            x = layer(x)
            if name in layers:
                features[layers[name]] = x

        return features

    def gram_matrix(self, tensor):
        """ Calculate the Gram Matrix of a given tensor
            Gram Matrix: https://en.wikipedia.org/wiki/Gramian_matrix
        """

        # get the batch_size, depth, height, and width of the Tensor
        _, d, h, w = tensor.size()

        # reshape so we're multiplying the features for each channel
        tensor = tensor.view(d, h * w)

        # calculate the gram matrix
        gram = torch.mm(tensor, tensor.t())

        return gram