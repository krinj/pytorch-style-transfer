#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Preload the VGG model (for the docker build).
"""

from torchvision import models

if __name__ == "__main__":
    vgg = models.vgg19(pretrained=True).features
