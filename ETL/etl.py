import re, datetime
from sysmessages import ILLEGAL_ARGUMENT
from functions import DATEPATTERN, MONEYPATTERN
from functions import moneytofloat, datestrtodate






class AtlasSignatureException:
    def __init__(self, *args: object) -> None:
        super().__init__(*args)






class AtlasItemDeTransacao:
    def __init__(self, txdate, ptacod, txvalue, opername) -> None:
        if txdate is None:
            raise Exception(ILLEGAL_ARGUMENT.format("txdate"))
        if ptacod is None:
            raise Exception(ILLEGAL_ARGUMENT.format("ptacod"))
        if txvalue is None:
            raise Exception(ILLEGAL_ARGUMENT.format("txvalue"))
        if opername is None:
            raise Exception(ILLEGAL_ARGUMENT.format("opername"))
        
        self.ptacod = ptacod
        self.opername = opername
        self.strtxvalue = txvalue
        self.txvalue = moneytofloat(txvalue)
        self.txdate = datestrtodate(txdate)

    def __eq__(self, value: object) -> bool:
        if value is None :
            raise Exception("Não é possível comparar este objeto com NULL (None)")
        
        if not isinstance(value, AtlasItemDeTransacao):
            raise Exception("Não é possível comparar este objeto com objetos desse tipo: " + value.__class__.__name__)
        
        if self.ptacod != value.ptacod:
            return False
        
        if self.txdate != value.txdate:
            return False
        
        if self.txvalue != value.txvalue:
            return False
        
        if self.opername != value.opername:
            return False
        
        return True
        
    def __ne__(self, value: object) -> bool:
        return not self.__eq__(value)
    
    def __gt__(self, value: object) -> bool:
        if value is None :
            raise Exception("Não é possível comparar este objeto com NULL (None)")
        
        if not isinstance(value, AtlasItemDeTransacao):
            raise Exception("Não é possível comparar este objeto com objetos desse tipo: " + value.__class__.__name__)
        
        if self.ptacod > value.ptacod:
            return True
        
        if self.ptacod == value.ptacod and self.txdate > value.txdate:
            return True
        
        if self.ptacod == value.ptacod and self.txdate == value.txdate and self.opername > value.opername:
            return True
        
        if self.ptacod == value.ptacod and self.txdate == value.txdate and self.opername == value.opername and self.txvalue > value.txvalue:
            return True
        
        return False
    
    def __lt__(self, value: object) -> bool:
        if value is None :
            raise Exception("Não é possível comparar este objeto com NULL (None)")
        
        if not isinstance(value, AtlasItemDeTransacao):
            raise Exception("Não é possível comparar este objeto com objetos desse tipo: " + value.__class__.__name__)
        
        if self.ptacod < value.ptacod:
            return True
        
        if self.ptacod == value.ptacod and self.txdate < value.txdate:
            return True
        
        if self.ptacod == value.ptacod and self.txdate == value.txdate and self.opername < value.opername:
            return True
        
        if self.ptacod == value.ptacod and self.txdate == value.txdate and self.opername == value.opername and self.txvalue < value.txvalue:
            return True
        
        return False
    
    def __hash__(self) -> int:
        vlr = "{0}:{1}:{2}:{3}:{4}".format(self.__class__.__name__, self.ptacod, self.txdate, self.opername, self.strtxvalue)
        return hash(vlr)
    
    def __str__(self) -> str:
        vlr = "ITEM ATLAS - CNP {0} - DATA {1} - {2} - VLR R$ {3}"
        vlr1 = vlr.format(self.ptacod, self.txdate.strftime("%d/%m/%Y"), self.opername, self.txvaluestr)
        return vlr1
    





def isok_atlassignature(textfile:str) -> bool:
    pattern = r"^Data;Ponto de venda;Vendedor;Forma de pagamento;Qtd. de vendas;Ticket m.+dio;Total"
    newtextfile = textfile.strip()
    if re.search(pattern, newtextfile) is None:
        return False
    else:
        return True






def parse_atlasdata(textfile: str) -> list:
    textlines = textfile.split("\n")

    ctrl = set()
    result = list()
    for line in textlines:
        l1 = line.strip()

        if not re.search(r"Ponto de venda: CNP\s*-\s*\d\d\d", l1):
            continue

        (date, cnp, opername, paymentmethod, qtd, ticket, total) = l1.split(";")

        date1 = re.search(DATEPATTERN, l1).group()
        date2 = str(date1)

        cnp1 = re.search(r"\d{3}", cnp).group()
        cnp2 = str(cnp1)

        opname = re.sub(r"\"", "", opername)

        vlr1 = re.search(MONEYPATTERN, total).group()
        vlr2 = str(vlr1)

        txitem = AtlasItemDeTransacao(date2, cnp2, vlr2, opname)
        if txitem not in ctrl:
            ctrl.add(txitem)
            result.append(txitem)

    return result






def atlas_selectbydate(day:int, month:int, year:int, records:list) -> list:
    result = list()

    date = datetime.date(year, month, day)
    for r in records:
        if r.txdate == date:
            result.append(r)

    return result






def atlas_selectbycnp(cnp:int, records:list) -> list:
    result = list()

    for r in records:
        if r.ptacod == cnp:
            result.append(r)

    return result






def atlas_somatotal(records:list) -> float:
    soma = 0

    for r in records:
        soma = soma + r.txvalue

    return round(soma, 2)














if __name__ == "__main__":

    with open("atlasdata.txt", "r", encoding="utf-8") as ff:

        textfile = ff.read()
        records = parse_atlasdata(textfile)

        distinct_cnps = set()

        for rec in records:
            distinct_cnps.add(rec.ptacod)

        sum_ctrl = {}
        sortedrecs = sorted(distinct_cnps)
        for ptacod in sortedrecs:
            if ptacod not in sum_ctrl.keys():
                sum_ctrl[ptacod] = 0

        for rec in records:
            ptacod = rec.ptacod
            txvalue = rec.txvalue
            sum_ctrl[ptacod] = sum_ctrl[ptacod] + txvalue


        print("SOMA TOTAL, AGRUPADO POR CNP")
        print("--------------------------------------------------------")
        total_geral = 0
        for ptacod in sortedrecs:
            total = sum_ctrl[ptacod]
            total_geral = total_geral + sum_ctrl[ptacod]
            print("CNP {0} - R$ {1:.2f}".format(ptacod, total))


        print("TOTAL GERAL: R$ {0:.2f}".format(total_geral))

            

