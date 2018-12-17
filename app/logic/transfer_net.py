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
    K_IMAGE_MEAN = (0.485, 0.456, 0.406)
    K_IMAGE_SD = (0.229, 0.224, 0.225)

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
            transforms.Normalize(self.K_IMAGE_MEAN, self.K_IMAGE_SD)
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

        # Declare the members.
        self.content_features = None
        self.style_features = None
        self.style_grams = None
        self.target_tensor = None
        self.optimizer = None
        self.current_step = 0
        self.steps = 10

        Logger.field("Torch Device", self.device)

    def convert_image_to_tensor(self, image: np.ndarray):
        """ Converts a CV2/Numpy image into PyTorch format. """
        image_tensor = self.tensor_transform(image)
        image_tensor = image_tensor.unsqueeze(0)
        image_tensor = image_tensor.to(self.device)
        return image_tensor

    def load_image(self, image_path: str, gray: bool=False):
        """ Load an image from disk. """
        image = cv2.imread(image_path)
        return self.prepare_image(image, gray)

    def prepare_image(self, image: np.ndarray, gray: bool=False):
        """ Prepare the image for processing via our network. """
        image = cv2.resize(image, (self.K_IMAGE_SIZE, self.K_IMAGE_SIZE))
        if gray:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return self.convert_image_to_tensor(image)

    def convert_tensor_to_image(self, tensor):
        """ Display a tensor as an image. """

        image = tensor.to(self.K_TORCH_CPU).clone().detach()
        image = image.numpy().squeeze()
        image = image.transpose(1, 2, 0)
        image = image * np.array(self.K_IMAGE_SD) + np.array(self.K_IMAGE_MEAN)
        image = image.clip(0, 1)
        image *= 255
        image = image.astype(np.uint8)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        return image

    def prepare_network(self, content_image, style_image, steps: int=3000):

        content_tensor = self.prepare_image(content_image)
        style_tensor = self.prepare_image(style_image)

        self.content_features = self.get_features(content_tensor, self.vgg)
        self.style_features = self.get_features(style_tensor, self.vgg)
        self.style_grams = {
            layer: self.gram_matrix(self.style_features[layer]) for layer in self.style_features}

        self.target_tensor = content_tensor.clone().requires_grad_(True).to(self.device)

        self.optimizer = optim.Adam([self.target_tensor], lr=0.003)
        self.steps = steps
        self.current_step = 0

    def process(self, content_image, style_image):
        pass

    def step(self):

        # get the features from your target image
        target_features = self.get_features(self.target_tensor, self.vgg)

        # the content loss
        content_loss = torch.mean((target_features['conv4_2'] - self.content_features['conv4_2']) ** 2)

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
            style_gram = self.style_grams[layer]
            # the style loss for one layer, weighted appropriately
            layer_style_loss = self.style_weights[layer] * torch.mean((target_gram - style_gram) ** 2)
            # add to the style loss
            style_loss += layer_style_loss / (d * h * w)

        # calculate the *total* loss
        total_loss = self.content_weight * content_loss + self.style_weight * style_loss

        # update your target image
        self.optimizer.zero_grad()
        total_loss.backward()
        self.optimizer.step()
        print('Total loss: ', total_loss.item())
        self.current_step += 1

        return self.current_step / self.steps

    def get_current_target_image(self):
        """ Get the current target image. """
        return self.convert_tensor_to_image(self.target_tensor)

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
