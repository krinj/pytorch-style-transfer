#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Use the CLI to run the style transfer directly.
"""

import argparse
import cv2
from k_util.logger import Logger
from logic.transfer_net import TransferNet

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--content_image", type=str,
                        help="The content image to use.")
    parser.add_argument("-s", "--style_image", type=str,
                        help="The style image to use.")
    parser.add_argument("-e", "--epochs", type=int,
                        default=3000,
                        help="Number of epochs to run.")
    parser.add_argument("-o", "--output", type=str,
                        default="style_output.png",
                        help="Where to save the output.")
    return parser.parse_args()


args = get_args()
content_image = args.content_image
style_image = args.style_image
epochs = args.epochs
output = args.output


if __name__ == "__main__":

    if content_image is None or style_image is None:
        print("Usage: ./cmd_run_style_transfer "
              "-c <content_image_path> "
              "-s <style_image_path> "
              "-e <n_epochs>")
        exit(1)

    Logger.header("Running Style Transfer CLI")
    net = TransferNet()
    net.process(content_image, style_image, epochs)
    Logger.log("Style Transfer Complete")

    # Write the file.
    image = net.get_current_target_image()
    cv2.imwrite(output, image)
    Logger.field("Image Written", output)

