import os, random
from utils.AMMMGlobals import AMMMException
from dataclasses import dataclass
from utils.input_parser import DATParser


@dataclass
class InstanceGenerator:

    config: DATParser

    def generate(self):

        instances_dir = self.config.instancesDirectory
        file_name_prefix = self.config.fileNamePrefix
        file_extension = self.config.fileNameExtension
        num_instances = self.config.numInstances

        numOrders = self.config.numOrders

        minOrderProfit = self.config.minOrderProfit
        maxOrderProfit = self.config.maxOrderProfit

        minOrderLength = self.config.minOrderLength
        maxOrderLength = self.config.maxOrderLength

        minOrderSurface = self.config.minOrderSurface
        maxOrderSurface = self.config.maxOrderSurface

        minMinOrderDeliver = self.config.minMinOrderDeliver
        maxMaxOrderDeliver = self.config.maxMaxOrderDeliver

        numSlots = self.config.numSlots

        minSurfaceCapacity = self.config.minSurfaceCapacity
        maxSurfaceCapacity = self.config.maxSurfaceCapacity

        if not os.path.isdir(instances_dir):
            raise AMMMException('Directory(%s) does not exist' % instances_dir)

        for i in range(num_instances):

            instance_path = os.path.join(instances_dir, '%s_%d.%s' % (file_name_prefix, i, file_extension))
            f_instance = open(instance_path, 'w')

            profit = [0] * numOrders
            length = [0] * numOrders
            surface = [0] * numOrders
            min_deliver = [0] * numOrders
            max_deliver = [0] * numOrders

            for o in range(numOrders):
                profit[o] = random.randint(minOrderProfit, maxOrderProfit)
                length[o] = random.randint(minOrderLength, maxOrderLength)
                surface[o] = random.randint(minOrderSurface, maxOrderSurface)

                max_deliver[o] = random.randint(length[o], maxMaxOrderDeliver)
                min_deliver[o] = random.randint(minMinOrderDeliver, max_deliver[o])

                assert min_deliver[o] <= max_deliver[o]
                assert max_deliver[o] >= length[o]

            surface_capacity = random.randint(minSurfaceCapacity, maxSurfaceCapacity)

            f_instance.write('n=%d;\n' % numOrders)
            f_instance.write('t=%d;\n' % numSlots)

            f_instance.write('profit=[%s];\n' % (' '.join(map(str, profit))))
            f_instance.write('length=[%s];\n' % (' '.join(map(str, length))))
            f_instance.write('min_deliver=[%s];\n' % (' '.join(map(str, min_deliver))))
            f_instance.write('max_deliver=[%s];\n' % (' '.join(map(str, max_deliver))))
            f_instance.write('surface=[%s];\n' % (' '.join(map(str, surface))))

            f_instance.write('surface_capacity=%d;\n' % surface_capacity)

            f_instance.close()
