import argparse
import random
import sys
import itertools
import requests

traffic_table = {
                2: 1, 3:1, 4:2, 5:2, 6:2, 7:3, 8:3, 9:3, 10:3,
                11:4, 12:4, 13:4, 14:5, 15:5, 16:6, 17:7, 18:8, 19:9
            }

class ParseUWP(object):
    def __init__(self, s):
        self.uwp = s
        self.starport = s[0]
        self.size = int(s[1],16)
        self.atmosphere = int(s[2],16)
        self.hydrosphere = int(s[3],16)
        self.population = int(s[4],16)
        self.government = int(s[5],16)
        self.law = int(s[6],16)
        self.tech = int(s[8],16)

    @property
    def Ag(self):
        return self.atmosphere >= 4 and self.atmosphere <=9 and\
            self.hydrosphere >= 4 and self.hydrosphere <=8 and\
                self.population >=5 and self.population<=7

    @property
    def As(self):
        return self.size==0 and self.atmosphere==0 and self.hydrosphere ==0

    @property
    def Ba(self):
        return self.population==0 and self.government==0 and self.law==0

    @property
    def De(self):
        return self.atmosphere >= 2 and self.hydrosphere==0

    @property
    def Fl(self):
        return self.atmosphere>=10 and self.hydrosphere>=1

    @property
    def Ga(self):
        return self.size>=6 and self.size <=8 and self.atmosphere in [5,6,8] and\
            self.hydrosphere >= 5 and self.hydrosphere <=7

    @property
    def Hi(self):
        return self.population>=9

    @property
    def Ht(self):
        return self.tech>=12

    @property
    def Ie(self):
        return self.atmosphere in [0,1] and self.hydrosphere>=1

    @property
    def In(self):
        return self.atmosphere in [0,1,2,4,7,9] and self.population>=9

    @property
    def Lo(self):
        return self.population <= 3

    @property
    def Lt(self):
        return self.tech <= 5

    @property
    def Na(self):
        return self.atmosphere in [0,1,2,3] and self.hydrosphere in [0,1,2,3] and self.population <= 6

    @property
    def Ni(self):
        return self.population <= 6

    @property
    def Po(self):
        return self.atmosphere>=2 and self.atmosphere<=5 and self.hydrosphere<=3

    @property
    def Ri(self):
        return self.atmosphere>=6 and self.atmosphere<=8 and self.population>=6 and self.population<=8 and\
            self.government>=4 and self.government<=9

    @property
    def Va(self):
        return self.atmosphere==0

    @property
    def Wa(self):
        return self.hydrosphere>=10
        
def UWPFromInternet(name):
    get = requests.get("https://travellermap.com/api/search", params={'q':name})
    uwp = get.json()['Results']['Items'][0]['World']['Uwp']
    return ParseUWP(uwp)

class GenerateTrade(object):
    def __init__(self, args):
        if args.search:
            self._source = UWPFromInternet(args.source[0])
            self._dest = UWPFromInternet(args.dest[0])
        else:
            self._source = ParseUWP(args.UWP[0])
            self._dest = ParseUWP(args.UWP[0])
        self._jump = args.jump
        self._broker = args.broker if args.broker else 0
        self._carouse = args.carouse if args.carouse else 0
        self._is_amber = args.amber
        self._is_red = args.red
        self._seed = args.seed[0] if args.seed else random.randint(1, sys.maxsize)
        self._prng = random.Random(self._seed)
        self._steward = args.steward if args.steward else -3
        self._hide = args.hide
        self._navy_rank = args.navy_rank if args.navy_rank else 0
        self._soc = args.soc if args.soc else 0

    @property
    def uwp(self):
        return self._source.uwp

    @property
    def seed(self):
        return str(self._seed) + ", broker effect " + str(self._broker) +", carouse effect " + str(self._carouse) + ", steward modifier " + str(self._steward)

    def d(self, n=1):
        if n == 0:
            return 0
        accumulator = 0
        for i in range(n):
            accumulator += self._prng.randint(1,6)
        return accumulator

    def dm(self, mod):
        return self.d(2)+mod

    def d66(self):
        return self.d()*10+self.d()

    def generate_passage(self, modifier=-4):
        modifiers = self._steward - modifier + self._carouse
        if self._source.population < 1:
            modifiers -=4
        elif self._source.population in [6,7]:
            modifiers +=1
        elif self._source.population >= 8:
            modifiers += 3

        if self._dest.population < 1:
            modifiers -= 4
        elif self._dest.population in [6,7]:
            modifiers += 1
        elif self._source.population >= 8:
            modifiers += 3

        if self._source.starport == 'A':
            modifiers += 2
        elif self._source.starport == 'B':
            modifiers += 1
        elif self._source.starport == 'E':
            modifiers -= 1
        elif self._source.starport == 'X':
            modifiers -= 3

        if self._source.starport == 'A':
            modifiers += 2
        elif self._source.starport == 'B':
            modifiers += 1
        elif  self._source.starport == 'E':
            modifiers -= 1
        elif self._source.starport == 'X':
            modifiers -= 3

        if self._is_amber:
            modifiers += 1
        elif self._is_red:
            modifiers -= 4

        dice_roll = self.dm(modifiers)
        if dice_roll <= 1:
            return []
        elif dice_roll >= 20:
            return self.d(10)
        else:
            return self.d(traffic_table[dice_roll])

    def generate_individual_passenger(self):
        dice_roll = self.d66()
        table = {
            11:"Refugee, political",
            12:"Refugee, economic",
            13: "Starting a new life",
            14: "Mercenary",
            15: "Spy",
            16: "Corporate",
            21: "Out to see the universe",
            22: "Tourist",
            23: "Yokel",
            24: "Adventurer",
            25: "Explorer",
            26: "Claustrophobic",
            31: "Mother",
            32: "Stowaway",
            33: "Possesses something dangerous",
            34: "Causes trouble",
            35: "Unusually handsome",
            36: "Mechanic or engineer",
            41: "Ex-Scout",
            42: "Wanderer",
            43: "Thief",
            44: "Scientist",
            45: "Journalist",
            46: "Entertainer",
            51: "Gambler",
            52: "Rich noble - complainer",
            53: "Rich noble - eccentric",
            54: "Rich noble - raconteur",
            55: "Diplomat on a mission",
            56: "Agent on a mission",
            61: "Patron",
            62: "Alien",
            63: "Bounty Hunter",
            64: "On the run",
            65: "Wants to be on this ship in particular",
            66: "Hijacker or pirate"
        }
        
        result = table[dice_roll]
        if dice_roll in [15,33,34,43,56,64,66]:
            if not self._hide:
                result += " (declared as %s)" % self.generate_individual_passenger()
            else:
                result = self.generate_individual_passenger()
        elif dice_roll in [32]:
            if not self._hide:
                result == " (not declared)"
            else:
                result = ""
        return result
        
    def freight_traffic_dm(self):
        modifier = 0
        if self._source.population <= 1:
            modifier -=4
        elif self._source.population in [6,7]:
            modifier += 2
        elif self._source.population >= 8:
            modifier += 4

        if self._dest.population <= 1:
            modifier -= 4
        elif self._dest.population in [6,7]:
            modifier += 2
        elif self._dest.population >= 8:
            modifier += 4

        if self._source.starport == 'A':
            modifier += 2
        elif self._source.starport == 'B':
            modifier += 1
        elif self._source.starport == 'E':
            modifier -= 1
        elif self._source.starport == 'X':
            modifier -= 3

        if self._dest.starport == 'A':
            modifier += 2
        elif self._dest == 'B':
            modifier += 1
        elif self._dest.starport == 'E':
            modifier -= 1
        elif self._dest.starport == 'X':
            modifier -= 3

        if self._source.tech <= 6:
            modifier -=1
        elif self._source.tech >= 9:
            modifier +=2

        if self._dest.tech <= 6:
            modifier -= 1
        elif self._dest.tech >= 9:
            modifier += 2

        if self._is_red:
            modifier -= 6
        elif self._is_amber:
            modifier -= 2
        return modifier
    
    def generate_freight(self, type_='minor'):
        modifier = 0 + self._broker
        if type_ == 'major':
            modifier -=4
        if type_ == 'incidental':
            modifier +=2
        modifier += self.freight_traffic_dm()

        dice_roll = self.dm(modifier)
        if dice_roll <= 1:
            number_packages = 0
        elif dice_roll >= 20:
            number_packages = self.d(10)
        else:
            number_packages = self.d(traffic_table[dice_roll])

        freight = []
        for i in range(number_packages):
            if type_ == 'major':
                weight = self.d()*10
            elif type_ == 'minor':
                weight = self.d()*5
            else:
                weight = self.d()
            contents = self.generate_freight_contents()
            if 'Illegal' in contents:
                if not self._hide:
                    contents += " (declared as %s)" % self.generate_freight_contents()
                else:
                    contents = self.generate_freight_contents()
            freight.append((type_+'#'+str(i+1),weight,contents))
        return freight

    def generate_freight_contents(self):
        dice_roll = self.d66()
        table = {
            11:'Common Electronics', 12:'Common Industrial Goods', 13:'Common Manufactured',
            14:'Common Raw Materials', 15:'Common Consumable', 16:'Common Ore',
            21:'Advanced Electronics', 22:'Advanced Machine Parts', 23:'Advanced Manufactured',
            24:'Advanced Weapons', 25:'Advanced Vehicles', 26:'Biochemicals',
            31:'Crystals and Gems', 32:'Cybernetics', 33:'Live Animals',
            34:'Luxury Consumables', 35:'Luxury Goods', 36:'Medical Supplies',
            41:'Petrochemicals',42:'Pharmacuticals',43:'Polymers',44:'Precious Metals',
            45:'Radioactives',46:'Robots',51:'Spices',52:'Textiles',
            53:'Uncommon Ore',54:'Uncommon Raw Materials',55:'Wood',56:'Vehicles',
            61:'Illegal Biochemicals',62:'Illegal Cybernetics',63:'Illegal Drugs',
            64:'Illegal Luxuries',65:'Illegal Weapons',66:'Exotics'
        }
        return table[dice_roll]

    def high_passage_price(self):
        table = [
            8500,12000,20000,41000,45000,470000            
        ]
        return table[self._jump]

    def middle_passage_price(self):
        table = [6200,9000,15000,31000,34000,350000]
        return table[self._jump]

    def basic_passage_price(self):
        table = [2200,2900,4400,8600,9400,93000]
        return table[self._jump]

    def low_passage_prices(self):
        table = [700,1300,2200,4300,13000,96000]
        return table[self._jump]

    def freight_prices(self):
        table=[1000,1600,3000,7000,7700,86000]
        return table[self._jump]

    def common_cargo(self):
        available = {
            "Common Electronics":self.d(2)*10,
            "Common Industrial Goods":self.d(2)*10,
            "Common Manufactured Goods":self.d(2)*10,
            "Common Raw Materials":self.d(2)*20,
            "Common Consumables":self.d(2)*20,
            "Common Ore":self.d(2)*20
        }
        if self._source.In or self._source.Ht:
            available["Advanced Electronics"] = self.d()*5
            available["Advanced Machine Parts"]=self.d()*5
            available["Advanced Manufactured Goods"]=self.d()*5
            available["Advanced Weapons"]=self.d()*5
            available["Advanced Vehicles"]=self.d()*5

        if self._source.Ag or self._source.Wa:
            available["Biochemicals"] = self.d()*5

        if self._source.As or self._source.De or self._source.Ie:
            available["Crystals"] = self.d()*5

        if self._source.Ht:
            available["Cybernetics"] = self.d()*5

        if self._source.Ag or self._source.Ga:
            available["Live Animals"] = self.d()*10

        if self._source.Ag or self._source.Ga or self._source.Wa:
            available["Luxury Consumables"] = self.d()*10

        if self._source.Hi:
            available["Luxury Goods"] = self.d()

        if self._source.Ht or self._source.Hi:
            available["Medical Supplies"] = self.d()*5

        if self._source.De or self._source.Fl or self._source.Ie or self._source.Wa:
            available["Petrochemicals"] = self.d()*10

        if self._source.As or self._source.De or self._source.Hi or self._source.Wa:
            available["Pharmacuticals"] = self.d()

        if self._source.In:
            available['Polymers'] = self.d()*10

        if self._source.As or self._source.De or self._source.Ie or self._source.Fl:
            available["Precious Metals"] = self.d()

        if self._source.As or self._source.De or self._source.Lo:
            available["Radioactives"] = self.d()

        if self._source.In:
            available["Robots"] = self.d()*5

        if self._source.Ga or self._source.De or self._source.Wa:
            available["Spices"] = self.d()*10

        if self._source.Ag or self._source.Ni:
            available["Textiles"] = self.d()*20

        if self._source.As or self._source.Ie:
            available["Uncommon Ore"] = self.d()*20

        if self._source.Ag or self._source.De or self._source.Wa:
            available["Uncommon Raw Materials"] = self.d()*10

        if self._source.Ag or self._source.Ga:
            available["Wood"] = self.d()*20

        if self._source.In or self._source.Ht:
            available["Vehicles"] = self.d()*10

        if self._source.Ag or self._source.Wa:
            available["Illegal Biochemicals"] = self.d()*5

        if self._source.Ht:
            available["Illegal Cybernetics"] = self.d()

        if self._source.As or self._source.De or self._source.Hi or self._source.Wa:
            available["Illegal Drugs"] = self.d()

        if self._source.Ag or self._source.Ga or self._source.Wa:
            available["Illegal Luxuries"] = self.d()

        if self._source.In or self._source.Ht:
            available["Illegal Weapons"] = self.d()
        
        return available
            
    def rare_cargo(self):
        table = {
            11:('Common Electronics',2,10), 12:('Common Industrial Goods',2,10),
            13:('Common Manufactured',2,10),14:('Common Raw Materials',2,20), 
            15:('Common Consumable',2,20), 16:('Common Ore',2,20),
            21:('Advanced Electronics',1,5), 22:('Advanced Machine Parts',1,5), 
            23:('Advanced Manufactured',1,5),24:('Advanced Weapons',1,5), 
            25:('Advanced Vehicles',1,5), 26:('Biochemicals',1,5),
            31:('Crystals and Gems',1,5),32:('Cybernetics',1,1), 
            33:('Live Animals',1,10),34:('Luxury Consumables',1,10), 
            35:('Luxury Goods',1,1), 36:('Medical Supplies',1,5),
            41:('Petrochemicals',1,10),42:('Pharmacuticals',1,1),
            43:('Polymers',1,10),44:('Precious Metals',1,1),
            45:('Radioactives',1,1),46:('Robots',1,5),
            51:('Spices',1,10),52:('Textiles',1,20),
            53:('Uncommon Ore',1,20),54:('Uncommon Raw Materials',1,10),
            55:('Wood',1,20),56:('Vehicles',1,10),
            61:('Illegal Biochemicals',1,5),62:('Illegal Cybernetics',1,1),
            63:('Illegal Drugs',1,1),64:('Illegal Luxuries',1,1),
            65:('Illegal Weapons',1,5),
            66:('Exotics',1,1)
        }
        rares = {}
        number_of_rares = self.d()
        for _ in range(number_of_rares):
            row = table[self.d66()]
            rares[row[0]] = rares.get(row[0],0) + self.d(row[1])*row[2]
        return rares

    def speculative_cargo(self):
        available = self.common_cargo()
        rare = self.rare_cargo()
        for k in rare.keys():
            available[k] = available.get(k,0) + rare[k]

        return available

    def generate_mail(self):
        modifier = self.freight_traffic_dm() + self._navy_rank + self._soc
        if self._source.tech <= 5:
            modifier -= 4
        if self._dest.tech <= 5:
            modifier -= 4
        dice_roll = self.dm(modifier)
        if dice_roll >= 12:
            return self.d()
        else:
            return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate trade and passengers for Mongoose 2e')
    parser.add_argument('source', nargs=1, help="The UWP for the source world")
    parser.add_argument('dest', nargs=1, help="The UWP for the destination world")
    parser.add_argument('jump', type=int, help='the distance to jump')
    parser.add_argument('--search', dest='search', action='store_true', help="Search traveller maps for the World UWPs")
    parser.add_argument('--amber', dest='amber', action='store_true', help='If the source world is amber')
    parser.add_argument('--red', dest='red', action='store_true', help='If either of the worlds is red')
    parser.add_argument('--seed', type=int, nargs=1, help="An optional PRNG seed")
    parser.add_argument('--steward', type=int, help='Steward modifier')
    parser.add_argument('--broker', type=int, help='The effect of a skillcheck for looking for cargo')
    parser.add_argument('--carouse', type=int, help='The effect of a skillcheck for looking for passengers')
    parser.add_argument('--hide', dest='hide', action='store_true', help='Hide illegal and problematic cargo behind a different description')
    parser.add_argument('--passengers', dest='get_passengers', action='store_true')
    parser.add_argument('--freight', dest='get_freight', action='store_true')
    parser.add_argument('--cargo', dest='get_cargo', action='store_true')
    parser.add_argument('--mail', dest='get_mail', action='store_true')
    parser.add_argument('--navy-rank', type=int, help="The highest navy or scout rank")
    parser.add_argument('--soc', type=int, help='The highest social standing DM')


    args = parser.parse_args()
    app = GenerateTrade(args)
    
    if not args.search:
        print("Available for %s->%s (seed %s)" % (args.source[0], args.dest[0], app.seed))
    else:
        print("Available for %s (%s)->%s (%s), (seed %s)" % (
            args.source[0], app._source.uwp, args.dest[0], app._dest.uwp, app.seed
        ))

    if args.get_passengers:
        print("\n---High Passengers (at %dcr)" % app.high_passage_price())
        high_passengers = app.generate_passage(-4)
        for _ in range(high_passengers):
            text = app.generate_individual_passenger()
            if text == "":
                continue
            else:
                print(text)

        print ("\n--Middle Passage (at %dcr)" % app.middle_passage_price())
        middle_passengers = app.generate_passage(0)
        for _ in range(middle_passengers):
            text = app.generate_individual_passenger()
            if text == "":
                continue
            else:
                print(text)

        print ("\n--Steerage/Basic Passage (at %dcr)" % app.basic_passage_price())
        basic_passengers = app.generate_passage(0)
        for _ in range(basic_passengers):
            text = app.generate_individual_passenger()
            if text == "":
                continue
            else:
                print(text)

        print ("\n---Low Passengers (at %dcr)" % app.low_passage_prices())
        print(app.generate_passage(1))

    if args.get_freight:
        print('\n---Freight (at %dcr/dton)' % app.freight_prices())
        major_freight = app.generate_freight('major')
        minor_freight = app.generate_freight('minor')
        incidental_freight = app.generate_freight('incidental')
        for i,weight,contents in itertools.chain(major_freight, minor_freight, incidental_freight):
            print("%s: %d dTons of %s (at %dcr)" % (i, weight, contents, app.freight_prices()*weight))

    if args.get_cargo:
        print('\n---Speculative Goods Available')
        cargo = app.speculative_cargo()
        for name in cargo.keys():
            print ("%s, %d dtons max" % (name, cargo[name]))

    if args.get_mail:
        mail = app.generate_mail()
        print('\n---Mail')
        if mail == 0:
            print("Mail NOT available at Navy/Scout Rank %s, Soc DM %s" % (args.navy_rank, args.soc))
        else:
            print("Mail IS available at Navy/Scout Rank %s, Soc DM %s" % (args.navy_rank, args.soc))
            print("%d Containers, %d dtons, all or none" % (mail, mail * 5))
