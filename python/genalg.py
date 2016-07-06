from __future__ import division

import copy

import numpy as np


class GenAlg(object):
    EPS = 1e-4

    def __init__(self, chrom_cls, pool_size=40, max_gen=None, select_ratio=0.7,
                 progress=False, interval=20, **chrom_kwargs):
        np.random.seed(0)

        self.max_gen = max_gen
        self.select_ratio = select_ratio
        self.progress = progress
        self.interval = interval

        self.pool_size = pool_size
        self.pool = np.array([chrom_cls(**chrom_kwargs)
                              for _ in range(pool_size)])

    def evolve(self):
        gen = 0
        select_size = np.floor(self.select_ratio * self.pool_size)
        select_size += select_size % 2
        select_size = int(min(select_size, self.pool_size))

        while self.max_gen is None or gen < self.max_gen:
            if self.progress and gen % self.interval == 0:
                fits = np.array([chrom.fitness() for chrom in self.pool])
                print("Generation {}".format(gen))
                print("\tFitness min/max/mean {:.4f} {:.4f} {:.4f}"
                      .format(fits.min(), fits.max(), fits.mean()))
                best = min(self.pool)

                best.log(gen)

            best, worst = GenAlg.get_children(self.pool, select_size)
            children = []
            for b1, b2 in np.split(best, select_size / 2):
                c1 = Chromosone.crossover(b1, b2)
                c2 = Chromosone.crossover(b2, b1)

                c1.mutate()
                c2.mutate()

                children.append(c1)
                children.append(c2)

            for w, c in zip(worst, children):
                w.replace(c)

            fittest = min(self.pool)
            if fittest.fitness() == 0 and fittest.valid:
                return fittest

            gen += 1

    @staticmethod
    def get_children(pool, num):
        worst_fits = np.array([chrom.fitness() + GenAlg.EPS
                               for chrom in pool])
        best_fits = 1 / worst_fits

        worst_fits /= sum(worst_fits)
        best_fits /= sum(best_fits)

        best = np.random.choice(pool, num, replace=True, p=best_fits)
        worst = np.random.choice(pool, num, replace=True, p=worst_fits)

        return best, worst


class Chromosone(object):
    def __init__(self, ngenes, gene_bits, crossover_rate=0.7,
                 mutate_rate=0.001):
        self.ngenes = ngenes
        self.gene_bits = gene_bits

        nbits = ngenes * gene_bits
        nbytes = nbits // 8 + 1

        rand_data = (np.random.rand(nbytes) * 255).astype('uint8')
        self.genes = np.unpackbits(rand_data).astype('bool')[:nbits]

        self.crossover_rate = crossover_rate
        self.mutate_rate = mutate_rate

        self._recalc = True
        self._fit = None

    def __lt__(self, other):
        return self.fitness() < other.fitness()

    @staticmethod
    def crossover(left, right):
        new = copy.deepcopy(left)

        if np.random.random() <= left.crossover_rate:
            new._recalc = True

            start = np.random.randint(len(new.genes))
            new.genes[start:] = right.genes[start:]

        return new

    def mutate(self):
        for idx, bit in enumerate(self.genes):
            if np.random.random() <= self.mutate_rate:
                self._recalc = True
                self.genes[idx] = not bit

    def replace(self, other):
        self.genes = other.genes
        self._recalc = True
