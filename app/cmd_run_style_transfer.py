#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
<ENTER DESCRIPTION HERE>
"""

from transfer_net import TransferNet

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


if __name__ == "__main__":
    print("Running Style Transfer App")
    net = TransferNet()
    net.process("../input/janelle.png", "../input/kahlo.jpg")
