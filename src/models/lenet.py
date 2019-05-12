from collections import OrderedDict
import torch.nn as nn

from .hydra_base import Hydra, Block


class Flatten(nn.Module):
    def forward(self, x):
        return x.view(x.size(0), -1)


class LeHydra(Hydra):
    """An example of a simple LeNet, written in Hydra API
    """
    def __init__(self, heads):
        super().__init__()

        # Defining body layers and weights
        layer1 = Block(nn.Sequential(OrderedDict([
            ('conv', nn.Conv2d(1, 20, 5)),
            ('relu', nn.ReLU()),
            ('pool', nn.MaxPool2d(2))
        ])), with_bn_pillow=False)
        layer2 = Block(nn.Sequential(OrderedDict([
            ('conv', nn.Conv2d(20, 50, 5)),
            ('relu', nn.ReLU()),
            ('pool', nn.MaxPool2d(2)),
        ])), with_bn_pillow=False)
        layer3 = Block(nn.Sequential(OrderedDict([
            ('flatten', Flatten()),
            ('fc', nn.Linear(4*4*50, 500)),
            ('relu', nn.ReLU())
        ])), with_bn_pillow=False)

        # Register body layers and stack them
        x = self.add_block(layer1)
        x = self.add_block(layer2).stack_on(x)
        x = self.add_block(layer3).stack_on(x)

        # Head constructor
        def define_head(n_classes):
            return Block(nn.Sequential(OrderedDict([
                    ('fc', nn.Linear(500, n_classes)),
                    ('softmax', nn.LogSoftmax(dim=1))])),
                with_bn_pillow=False)

        # Define the heads and stack them on
        for head in heads:
            module = define_head(head['n_classes'])
            h = self.add_head(module, head['task_id'])
            h.stack_on(x)

        # Don't forget to build the model
        self.build()
