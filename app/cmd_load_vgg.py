#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
<ENTER DESCRIPTION HERE>
"""

from torchvision import models

if __name__ == "__main__":
    vgg = models.vgg19(pretrained=True).features
