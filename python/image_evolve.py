from __future__ import division

import argparse
import os
import shutil

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageStat

import genalg as ga


class ImageChromo(ga.Chromosone):
    COLOR = {'num': 3, 'dtype': np.dtype('uint8')}
    POS = {'num': 2, 'dtype': np.dtype('uint32')}
    SIZE = {'num': 1, 'dtype': np.dtype('uint32')}

    BITS_PER_GENE = (COLOR['num'] * COLOR['dtype'].itemsize * 8
                     + POS['num'] * POS['dtype'].itemsize * 8
                     + SIZE['num'] * SIZE['dtype'].itemsize * 8)

    def __init__(self, ngenes, target, copying=False):
        super(ImageChromo, self).__init__(ngenes, ImageChromo.BITS_PER_GENE)

        if not copying:
            self.target = Image.open(target)
            self.width, self.height = self.target.size
            self.image = Image.new('RGB', self.target.size)
            self.draw = ImageDraw.Draw(self.image)

            self.dir = os.path.join('..', 'output',
                                    os.path.splitext(os.path.basename(target))[0])
            shutil.rmtree(self.dir, ignore_errors=True)
            os.makedirs(self.dir)

    def __deepcopy__(self, memo):
        new = ImageChromo(self.ngenes, self.target, True)

        new.target = self.target.copy()
        new.width, new.height = self.target.size
        new.image = self.image.copy()
        new.draw = ImageDraw.Draw(new.image)

        new.genes = np.copy(self.genes)

        return new

    def fitness(self):
        if not self._recalc:
            return self._fit

        self._recalc = False
        self.decode()

        dif = ImageChops.difference(self.target, self.image)
        self._fit = sum(ImageStat.Stat(dif).sum2)
        return self._fit

    def decode(self):
        self.draw.rectangle(((0, 0), self.image.size), fill=(0, 0, 0))
        c_data = ImageChromo.COLOR
        p_data = ImageChromo.POS
        s_data = ImageChromo.SIZE

        c_size = c_data['num'] * c_data['dtype'].itemsize * 8
        p_size = p_data['num'] * p_data['dtype'].itemsize * 8

        for gene in np.split(self.genes, self.ngenes):
            color = self._decode_gene(gene[:c_size], **c_data)
            pos = self._decode_gene(gene[c_size + 1:c_size + p_size], **p_data)
            size = self._decode_gene(gene[c_size + p_size + 1:], **s_data)

            pos = (pos.astype(float) / np.iinfo(p_data['dtype']).max) * self.image.size
            size = (size.astype(float) / np.iinfo(s_data['dtype']).max) * min(self.image.size)

            self.draw.ellipse((tuple(pos), tuple(pos + size)),
                              fill=tuple(color))

    @staticmethod
    def _decode_gene(gene, num, dtype):
        bytes = np.packbits(gene).tobytes()
        decoded = np.fromstring(bytes, dtype=dtype, count=num)
        return decoded if len(decoded) > 1 else decoded[0]

    def log(self, gen):
        path = os.path.join(self.dir, str(gen) + '.png')
        self.image.save(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('target')
    parser.add_argument('-m', '--max_gen', default=None, type=int)
    parser.add_argument('-i', '--interval', default=20, type=int)
    parser.add_argument('-p', '--progress', action='store_true')
    parser.add_argument('-s', '--select_ratio', default=0.3, type=float)
    parser.add_argument('-c', '--pool_size', default=30, type=int)
    parser.add_argument('-g', '--ngenes', default=300, type=int)

    kwargs = vars(parser.parse_args())

    ga = ga.GenAlg(ImageChromo, **kwargs)
    answer = ga.evolve()
