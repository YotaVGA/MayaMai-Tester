#!/usr/bin/python

# Copyright ® 2008-2009 Fulvio Satta
#
# If you want contact me, send an email to Yota_VGA@users.sf.net
#
# This file is part of MayaMai Tester
#
# MayaMay Tester is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MayaMay is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

#This work is based on a game of
#Roberto Rampini (http://www.robertorampini.it/).

from progressbar import *

class Solved(ProgressBarWidget):
    def update(self, progressbar):
        return '{}'.format(len(boards))

maxprogress = 1000000
bar = ProgressBar(widgets = ['Analysis: ', Percentage(), ' ',
                             Bar(left = '[', right = ']'),
                             ' Solved: ', Solved(),
                             '  ', ETA()],
                  maxval = maxprogress)
totalprogress = 0

#yellow, red, brown, blue, green
indexes = (
         8,  2,  3,  5, 4,  26,
        13, 22, 16, 19, 14, 10,
        24, 11, 23, 27,  7, 20,
         6, 15, 17, 18, 12, 30,
        25, 28, 21,  9, 29,  1)
rotations = (
        1, 2, 2, 2, 2, 0,
        1, 1, 1, 1, 0, 1,
        3, 0, 0, 3, 1, 2,
        3, 3, 2, 3, 3, 3,
        1, 1, 3, 3, 2, 1)
borders = (
        (4, 1, 2, 0, 3, 4), #up
        (4, 3, 0, 2, 1, 4), #down
        (3, 2, 4, 0, 1), #left
        (1, 0, 4, 2, 3)) #right

class Piece(tuple):
    def data(self):
        for i in range(5):
            if i not in self:
                l = list(range(5))
                del l[i]
                r = self.index(l[0])
                l2 = [self[(r + 1) % 4], \
                      self[(r + 2) % 4], \
                      self[(r + 3) % 4]]
                i2 = l.index(l2[0]) - 1
                if l2[1] < l2[2]:
                    i3 = 0
                else:
                    i3 = 1
                n = i * 6 + i2 * 2 + i3

                s = ""
                return n, r

    def __hash__(self):
        return self.data()[0]

    def __eq__(self, b):
        if b == None:
            return False
        return self.data()[0] == b.data()[0]

    def up(self):
        return self[(self.rot + 2) % 4]

    def down(self):
        return self[self.rot]

    def left(self):
        return self[(self.rot + 3) % 4]
    
    def right(self):
        return self[(self.rot + 1) % 4]

    def __str__(self, retRotation = True, retNumber = True):
        s = ''
        n, r = self.data()
        if retNumber:
            s += '{:2}'.format(indexes[n])
        if retRotation:
            s += (' ', 'r', 't', 'R')[(-rotations[n] + r + self.rot) % 4]
        return s

    def __repr__(self):
        return self.__str__(self)

class BoardList(list):
    def __repr__(self):
        return '---------------------------------\n'.join(map(repr, self))

class Board(set):
    def ups(self, x, y):
        if y == 0:
            return {borders[0][x]}
        v = self.table[x][y - 1]
        if v == None:
            return set(range(5))
        return {v.down()}

    def downs(self, x, y):
        if y == 4:
            return [borders[1][x]]
        v = self.table[x][y + 1]
        if v == None:
            return set(range(5))
        return {v.up()}

    def lefts(self, x, y):
        if x == 0:
            return [borders[2][y]]
        v = self.table[x - 1][y]
        if v == None:
            return set(range(5))
        return {v.right()}

    def rights(self, x, y):
        if x == 5:
            return {borders[3][y]}
        v = self.table[x + 1][y]
        if v == None:
            return set(range(5))
        return {v.left()}

    def fastGet(self, x, y):
        pl = set()
        for p in self:
            for r in range(4):
                l = [p[ r      % 4], \
                     p[(r + 1) % 4], \
                     p[(r + 2) % 4], \
                     p[(r + 3) % 4]]
                if l[0] not in self.downs(x, y):
                    continue
                if l[1] not in self.rights(x, y):
                    continue
                if l[2] not in self.ups(x, y):
                    continue
                if l[3] not in self.lefts(x, y):
                    continue
                new = Piece(p)
                new.rot = r
                pl.add(new)
        return pl

    def addPiece(self, p, x, y):
        self.discard(p)
        self.table[x][y] = p

    def getPieces(self, x, y):
        pl = set()
        for p in self.fastGet(x, y):
            lr = p[ p.rot      % 4], \
                 p[(p.rot + 1) % 4], \
                 p[(p.rot + 2) % 4], \
                 p[(p.rot + 3) % 4]

            if y != 0 and self.table[x][y - 1] == None:
                l2 = self.lefts (x, y - 1), \
                     self.rights(x, y - 1), \
                     self.ups   (x, y - 1)
                ls = set()
                for i in l2:
                    if len(i) == 1:
                        ls.add(list(i)[0])
                if lr[2] in ls:
                    continue

            if y != 4 and self.table[x][y + 1] == None:
                l2 = self.lefts (x, y + 1), \
                     self.rights(x, y + 1), \
                     self.downs (x, y + 1)
                ls = set()
                for i in l2:
                    if len(i) == 1:
                        ls.add(list(i)[0])
                if lr[0] in ls:
                    continue

            if x != 0 and self.table[x - 1][y] == None:
                l2 = self.downs(x - 1, y), \
                     self.lefts(x - 1, y), \
                     self.ups  (x - 1, y)
                ls = set()
                for i in l2:
                    if len(i) == 1:
                        ls.add(list(i)[0])
                if lr[3] in ls:
                    continue

            if x != 5 and self.table[x + 1][y] == None:
                l2 = self.downs (x + 1, y), \
                     self.rights(x + 1, y), \
                     self.ups   (x + 1, y)
                ls = set()
                for i in l2:
                    if len(i) == 1:
                        ls.add(list(i)[0])
                if lr[1] in ls:
                    continue

            pl.add(p)
        return pl

    def generateBoards(self, x, y, progress = 0):
        global n, totalprogress
        ps = self.getPieces(x, y)
        n = len(ps)
        if not n and progress:
            totalprogress += progress
            bar.update(totalprogress)
            return
        lastprogress = 0
        num = n
        for i, p in enumerate(ps):
            b = Board(self)
            b.table = [i[:] for i in self.table]
            b.addPiece(p, x, y)
            if progress:
                newprogress = (progress * (i + 1)) // num
                totalprogress += newprogress - lastprogress
                lastprogress = newprogress
                bar.update(totalprogress)
            yield b

    def __repr__(self):
        def formatname(elem):
            if elem == None:
                return ' N '
            return repr(elem)

        s = ''
        for y in range(5):
            for x in range(6):
                if x != 0:
                    s += ' ' * 3
                s += formatname(self.table[x][y])
            s += '\n'
        return s

board = Board()
for i in range(5):
    for j in range(3):
        for k in range(2):
            l = list(range(5))
            del l[i]
            if j >= 1:
                l[1], l[j + 1] = l[j + 1], l[1]
            if k:
                l[2], l[3] = l[3], l[2]
            p = Piece(l)
            p.rot = 0
            board.add(p)
board.table = [[None for i in range(5)] for j in range(6)]

pieceorder = (0, 0), (0, 1), (1, 0), (1, 1), (0, 2), (2, 0), (1, 2), (2, 1), \
             (0, 4), (0, 3), (3, 0), (5, 0), (4, 0), (1, 4), (1, 3), (3, 1), \
             (2, 2), (4, 1), (2, 3), (3, 2), (2, 4), (5, 1), (3, 4), (5, 2), \
             (3, 3), (4, 2), (4, 4), (5, 3), (4, 3), (5, 4)

def setup(order, base, progress):
    global totalprogress, n
    p = 0
    others = order[1:]
    if not others:
        p = progress
    it = base.generateBoards(order[0][0], order[0][1], p)
    first = True
    lastprogress = 0
    for pos, i in enumerate(it):
        if first:
            first = False
            num = n
        if (others):
            newprogress = (progress * (pos + 1)) // num
            p = newprogress - lastprogress
            lastprogress = newprogress
            for j in setup(others, i, p):
                yield j
        else:
            yield i
    if first and others and progress:
        totalprogress += progress
        bar.update(totalprogress)

boards = BoardList()
bar.start()
for b in setup(pieceorder, board, maxprogress):
    boards.append(b)
    bar.update(totalprogress)
bar.finish()

print(boards)
print("\n{} boards".format(len(boards)))
