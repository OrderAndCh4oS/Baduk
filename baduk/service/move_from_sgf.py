import os.path
import re

from baduk.constants.constants import ALPHA_KEY


class MovesFromSGF:

    def __init__(self, sgf):
        os.path.isfile(sgf)
        with open(sgf, 'r') as file:
            self.st = file.read().replace('\n', '')
        self.sgf_coordinates = []
        self.korschelt_coordinates = []
        self.extract_coordinates()

    def get_as_korschelt(self):
        return self.korschelt_coordinates

    def get_as_sgf(self):
        return self.sgf_coordinates

    def extract_coordinates(self):
        matches = self.find_moves_in_sgf()
        for match in matches:
            coordinate = match.groups()[0]
            self.sgf_coordinates.append(coordinate)
            self.korschelt_coordinates.append(self.sgf_to_korschelt(coordinate))

    def find_moves_in_sgf(self):
        return re.finditer(r";[BW]\[([a-z]{2})\]", self.st, re.MULTILINE)

    def sgf_to_korschelt(self, coordinate):
        column_value = ord(coordinate[0]) - ord('a')
        row_value = ord(coordinate[1]) - ord('a')
        column_key = ALPHA_KEY[column_value]
        row_key = row_value + 1
        return "%s%s" % (row_key, column_key)


if __name__ == '__main__':
    st = ";B[pd]BL[60];W[dp]WL[58];B[oq]BL[56];W[dc]WL[53];B[pn]BL[56];W[qf]WL[41];B[qe]BL[51];W[pf]WL[37];B[ld]BL[51];W[qj]WL[36];B[pk]BL[50];W[rl]WL[421];B[qk]BL[50];W[rk]WL[414];B[df]BL[22];W[gc]WL[397];B[pj]BL[2];W[qi]WL[395];B[pi]BL[578];W[qh]WL[394];B[ph]BL[503];W[nd]WL[385];B[oe]BL[464];W[oc]WL[380];B[pc]BL[462];W[ob]WL[379];B[pb]BL[461];W[lc]WL[379];B[kc]BL[458];W[lb]WL[374];B[kb]BL[457];W[ne]WL[358];B[of]BL[455];W[kd]WL[351];B[jd]BL[453];W[md]WL[350];B[ke]BL[452];W[le]WL[350];B[kd]BL[451];W[lf]WL[348];B[kf]BL[450];W[nf]WL[347];B[pg]BL[446];W[qg]WL[345];B[ng]BL[444];W[pe]WL[341];B[od]BL[442];W[qd]WL[339];B[qc]BL[441];W[rd]WL[338];B[rc]BL[441];W[re]WL[337];B[lg]BL[438];W[mf]WL[335];B[mg]BL[437];W[mc]WL[317];B[jp]BL[434];W[rp]WL[315];B[rn]BL[429];W[qq]WL[309];B[pr]BL[425];W[qr]WL[598];B[op]BL[423];W[pq]WL[598];B[or]BL[422];W[qo]WL[598];B[qn]BL[421];W[po]WL[598];B[on]BL[598];W[pp]WL[597];B[oo]BL[597];W[oh]WL[593];B[og]BL[595];W[ni]WL[589];B[mj]BL[593];W[nk]WL[581];B[nj]BL[591];W[cj]WL[575];B[di]BL[588];W[ci]WL[573];B[dj]BL[587];W[ch]WL[571];B[dh]BL[586];W[dk]WL[571];B[ek]BL[585];W[dl]WL[570];B[el]BL[584];W[em]WL[569];B[gl]BL[583];W[fj]WL[567];B[ej]BL[582];W[jh]WL[566];B[mi]BL[580];W[kg]WL[563];B[jg]BL[577];W[kh]WL[562];B[ig]BL[576];W[kj]WL[562];B[mk]BL[573];W[kl]WL[562];B[kn]BL[572];W[jm]WL[560];B[jn]BL[570];W[im]WL[559];B[gn]BL[566];W[fm]WL[558];B[gm]BL[564];W[fl]WL[557];B[fk]BL[564];W[gk]WL[556];B[hl]BL[563];W[gj]WL[596];B[fi]BL[559];W[gi]WL[594];B[fh]BL[556];W[gh]WL[594];B[gg]BL[556];W[hg]WL[591];B[hf]BL[599];W[fg]WL[590];B[hh]BL[598];W[ff]WL[590];B[eg]BL[596];W[ij]WL[587];B[il]BL[588];W[jk]WL[586];B[hi]BL[587];W[ik]WL[583];B[ii]BL[584];W[ji]WL[580];B[fe]BL[580];W[ge]WL[577];B[gf]BL[577];W[fd]WL[576];B[ee]BL[575];W[ce]WL[574];B[ed]BL[574];W[ec]WL[573];B[he]BL[572];W[gq]WL[572];B[iq]BL[570];W[ml]WL[568];B[nl]BL[569];W[mm]WL[567];B[nm]BL[569];W[mn]WL[566];B[mp]BL[567];W[lo]WL[565];B[lp]BL[566];W[ko]WL[564];B[jo]BL[566];W[kp]WL[563];B[kq]BL[566];W[lk]WL[558];B[li]BL[559];W[km]WL[555];B[ln]BL[556];W[lm]WL[548];B[mo]BL[552];W[lj]WL[546];B[ki]BL[545];W[jj]WL[597];B[jl]BL[536];W[cq]WL[592];B[hn]BL[532];W[dm]WL[590];B[hk]BL[519];W[hj]WL[588];B[in]BL[599];W[ih]WL[587];B[hg]BL[595];W[ib]WL[587];B[ic]BL[587];W[gd]WL[585];B[hc]BL[585];W[hb]WL[582];B[la]BL[580];W[ma]WL[579];B[ka]BL[579];W[ie]WL[578];B[hd]BL[572];W[gb]WL[577];B[na]BL[568];W[mb]WL[573];B[oa]BL[567];W[nb]WL[572];B[pa]BL[567];W[jb]WL[571];B[jc]BL[564];W[de]WL[565];B[dd]BL[559];W[cd]WL[564];B[ef]BL[558];W[cf]WL[563];B[dg]BL[556];W[cg]WL[563];B[hq]BL[554];W[fo]WL[563];B[gp]BL[551];W[fp]WL[562];B[go]BL[549];W[fq]WL[561];B[fn]BL[547];W[en]WL[559];B[gr]BL[547];W[fr]WL[557];B[hr]BL[547];W[fs]WL[556];B[gs]BL[545];W[sd]WL[555];B[sc]BL[541];W[ql]WL[595];B[pl]BL[538];W[qs]WL[589];B[rm]BL[533];W[sl]WL[587];B[ro]BL[532];W[sp]WL[584];B[so]BL[597];W[rj]WL[577];B[ps]BL[594];W[rq]WL[566];B[sr]BL[590];W[qm]WL[564];B[pm]BL[587];W[sm]WL[563];B[lh]BL[576];W[nn]WL[561];B[no]BL[573];W[ja]WL[547];B[if]BL[561];W[hm]WL[538];B[rr]BL[543];W[rs]WL[522];B[ss]BL[529];W[sq]WL[520];B[sr]BL[526];W[sn]WL[518];B[tt]BL[526];W[tt]WL[516];B[tt]BL[526]"
    moves = MovesFromSGF(st)
    for move in moves.get_as_korschelt():
        print(move)
