
# This alogotithm copes with the possibliity of more than one one to construct the build of an item
#i do make too many factories but that was the cost of trying all paths to fulfill  orders
# it is a bit of a mish mash of mutable and immutable - but the method names are always indicative
# orders may be muych more complicted than jus an order for a single thing and they may be fully or partially delivered

#  I have have considered and rejected some  optimization to sometimes use muteable factories to stop factories being copied too often
# I have used deep copy just to make sure some my imutables are imutable and implement deepcopy for imutables to return self as an optimization
import json
import copy

class Recipe:
    def __init__(self,name,title,consumes,produces,elapsedSecondsToExecute):
        self.name=name
        self.title = title
        self.consumes  =copy.deepcopy(consumes)
        self.produces  =copy.deepcopy(produces)
        self.elapsedSecondsToExecute =elapsedSecondsToExecute

    @classmethod
    def fromJsonObjAndName(cls,name,jsonObj):
        assert  isinstance(jsonObj,dict)
        return cls(name,jsonObj["title"],
               ItemTypeQuantities.fromQuantityByTypeNameDict(jsonObj["consumes"]),
               ItemTypeQuantities.fromQuantityByTypeNameDict(jsonObj["produces"]),
               jsonObj["time"])

    @classmethod
    def recipesfromJsonObj(cls,jsonObj):
        assert  isinstance(jsonObj,dict)
        recipes = [ ]
        return [Recipe.fromJsonObjAndName(key,jsonObj[key]) for key in jsonObj]

    def __str__(self):
        return "R("+ self.name + " consumes=" + str(self.consumes)+ " produces=" + str(self.produces)+")"

    def __eq__(self, other):
        if id(self)==id(other):
            return True
        elif type(other) is type(self):
            return vars(self).items() == vars(other).items()
        else:
            return False

    def __hash__(self):
        return hash(self.title) + hash(self.consumes)  +hash(self.produces)  + hash(self.elapsedSecondsToExecute)

    def canExecuteWithInventory(self,inventory):
        return inventory.subsumes(self.consumes)

    def producesOneOf(self,itemTypes):
        return self.produces.hasAnyOf(itemTypes)

    def __deepcopy__(self,memo):
        #Recipies are imputable so copy can be itself
        return self


class ItemTypeQuantities:
    def __init__(self, quantByItems = None):

        if(quantByItems is None):
            self.itemQuantityHeldByItemType = {}
        else:
            if isinstance(quantByItems,ItemTypeQuantities):
                self.itemQuantityHeldByItemType=copy.deepcopy(quantByItems.itemQuantityHeldByItemType)
            else:
                self.itemQuantityHeldByItemType = {ItemType(k):quantByItems[k]  for k in quantByItems }  # ensure I am immutable
        for  k in self.itemQuantityHeldByItemType:
            assert self.itemQuantityHeldByItemType[k]>=0
            assert k is not None

    @classmethod
    def fromJsonObj(cls,jsonObj):
        return cls.fromQuantityByTypeNameDict(jsonObj)

    @classmethod
    def fromQuantityByTypeNameDict(cls,quantityByTypeNameDict):        # Yes I know there may be no value in wrapping strings in itemtypes
        quantByItemType = {}
        for (name,quantity) in  quantityByTypeNameDict.items():
            quantByItemType[ItemType(name)]=quantity
        return cls(quantByItemType)

    def __str__(self):
        return  ",".join([str(k)+ "->" + str(v)  for (k,v) in self.itemQuantityHeldByItemType.items()])

    def numberOfItems(self):
        return sum(self.itemQuantityHeldByItemType.values(),0)

    def itemTypesPresent(self):
        return [itemType for itemType in self.itemQuantityHeldByItemType if self.quantityOfItemType(itemType) >0]

    def hasAnyOf(self,itemTypes):
       return len(set(self.itemTypesPresent()).intersection(itemTypes))!=0

    def quantityOfItemType(self,itemType):
        return self.itemQuantityHeldByItemType.get(itemType,0)

    def __eq__(self, other):
        if id(self)==id(other):
            return True
        elif type(other) is type(self):
            return vars(self).items() == vars(other).items()
        else:
            return False

    def __hash__(self):
        return hash(vars(self).items())

    def subsumes(self,other):
        for itemType in other.itemTypesPresent():
            if self.quantityOfItemType(itemType)  < other.quantityOfItemType(itemType) :
                return False
        return True
    def itemTypesNotSubsumedBy(self,other):
        return [itemType for itemType in self.itemTypesPresent() if self.quantityOfItemType(itemType) >  other.quantityOfItemType(itemType)]

    def withOneRemoved(self,itemType):
        quantByItemType = copy.deepcopy(self.itemQuantityHeldByItemType )
        assert quantByItemType.get(itemType,None) is not None
        quantByItemType[itemType]= quantByItemType[itemType] -1
        return ItemTypeQuantities(quantByItemType)


    def plus(self,other):
        keys = {k for k in self.itemQuantityHeldByItemType.keys()}.union( other.itemQuantityHeldByItemType.keys() )
        return ItemTypeQuantities({key: self.quantityOfItemType(key)+other.quantityOfItemType(key) for key in keys })

    def minus(self,other):
        keys = {k for k in self.itemQuantityHeldByItemType.keys()}.union( other.itemQuantityHeldByItemType.keys() )
        return ItemTypeQuantities({key: self.quantityOfItemType(key)-other.quantityOfItemType(key) for key in keys })

    def __deepcopy__(self,memo):
        #ItemTypeQuantities are imputable so copy can be itself
        return self

class ItemType:
    def __init__(self,name):
        if isinstance(name, ItemType) :
            self.name=name.name
        else:
            self.name=name
    def __deepcopy__(self,memo):
        #ItemType are imputable so copy can be itself
        return self

    def __str__(self):
        return "IT("+self.name + ")"

    def __eq__(self, other):
        if id(self)==id(other):
            return True
        if type(other) is type(self):
            return self.name == other.name
        else:
            return False

    def __hash__(self):
        return hash(self.name)

class Factory:

    def __init__(self,recipes,inventory):
        self.recipes=copy.deepcopy(recipes)
        self.inventory= copy.deepcopy(inventory)

    def __str__(self):
        return "F(inventory="+ str(self.inventory) +")"

    def deliveryAndFactoryAfterFulfillmentOrNoneNoneIfCant(self,fulfillmentPath):
        return fulfillmentPath.deliveryAndFactoryAfterFulfilmentOrNoneNone(self)

    def sizeOfInventory(self):
        return self.inventory.numberOfItems()

    def  hasItemTypeInInventory(self, itemType):
        return self.inventory.quantityOfItemType(itemType)>0

    def recipesThatCanBeExecuted(self):
        return [r for r in self.recipes if r.canExecuteWithInventory(self.inventory)]

    def recipesThatCanExecuteThatCanProduceItemsFrom(self,itemTypes):
        return [r for r in self.recipes if r.canExecuteWithInventory(self.inventory) and r.producesOneOf(set(itemTypes))]

    def itemTypesThatAreMisingAndPreventRecipesFormExecuting(self):
        listOFListOfItemTypes = [r.consumes.itemTypesNotSubsumedBy(self.inventory) for r in self.recipes]
        itemTypes = [item for sublist in listOFListOfItemTypes for item in sublist]
        return set(itemTypes)

    def __eq__(self, other):
        if id(self)==id(other):
            return True
        elif type(other) is type(self):
            return vars(self).items() == vars(other).items()
        else:
            return False

    def __hash__(self):
        return hash(vars(self).items())

    def excutePathReturningDeliveryOrNone(self,fulfillmentPath):  # a hack to make factories  change
        delivery = ItemTypeQuantities()
        (delivery,newFactory) = fulfillmentPath.deliveryAndFactoryAfterFulfilmentOrNoneNone(self)
        self.inventory=newFactory.inventory.deepCopy
        return delivery

    def bestFulfillmentPathForEachOrderInTurn(self,orders):
        f= self
        bestFulfillmentPathForEachOrderInTurn=list()
        for order in orders:
            best = f.bestFulfillmentPathForOrderOrNone(order);
            if best is not None:
                (delivery,f) = f.deliveryAndFactoryAfterFulfillmentOrNoneNoneIfCant(best)
            bestFulfillmentPathForEachOrderInTurn.append(best)
        return  bestFulfillmentPathForEachOrderInTurn

    def bestFulfillmentPathForOrderOrNone(self,order):
        paths = FulfillmentPath.fulfillmentPaths(order,self)
        if len(paths)==0 :
            return None
        best=paths[0]
        for p in paths[1:]:
            (db,fb)=self.deliveryAndFactoryAfterFulfillmentOrNoneNoneIfCant(best)
            (d,f)=self.deliveryAndFactoryAfterFulfillmentOrNoneNoneIfCant(p)
            if(db.numberOfItems() < d.numberOfItems()) :
                best=p
            elif db.numberOfItems() == d.numberOfItems() and  fb.sizeOfInventory()< f.sizeOfInventory():
                best=p
        return best

class Order:
    def __init__(self,required,allowPartialFulfillment):
        self.required = required
        self.allowPartialFulfillment = allowPartialFulfillment

    @classmethod
    def fromString(cls, orderString):
        amountXType=orderString.split()
        assert len(amountXType) == 2
        amount= int(amountXType[0].lower().replace("x",""))
        typeName=   amountXType[1]
        return cls(ItemTypeQuantities({typeName:amount}),True)

    @classmethod
    def fromStrings(cls,orderStrings):
        return [cls.fromString(s) for s in orderStrings ]

    def __eq__(self, other):
        if id(self)==id(other):
            return True
        elif type(other) is type(self):
            return vars(self).items() == vars(other).items()
        else:
            return False

    def __hash__(self):
        return hash(vars(self).items())

    def allFirstActions(self,factory):  # factory allows us to limit the possible first actions with out just tryng them ll
        # always deliver if possible
        # run any recipe that mught produce a new thing to deliver
        # run any recipe that creates items that the invetory does not have that prevets a recipe for runing
        # so either there is a  recipe that can run that will produce and item or there are items that need to be built
            # so attempting to run a reciept that might help another recipy run is a good thing
            # all recipes that can run but dont help an un runnable recipe dont help
        deliveryActions =  [DeliverAction(itemType) for itemType in self.required.itemTypesPresent() if factory.hasItemTypeInInventory(itemType)]

        recipesThatWillMakeSomethingNeeded = factory.recipesThatCanExecuteThatCanProduceItemsFrom(self.required.itemTypesPresent())
        recipesThatWillHelpARecipeRun  = factory.recipesThatCanExecuteThatCanProduceItemsFrom(factory.itemTypesThatAreMisingAndPreventRecipesFormExecuting())

      
        if len(deliveryActions)!=0:
            actions=[deliveryActions[0]]
        elif len(recipesThatWillMakeSomethingNeeded)  !=0:
            actions=   [ExecuteRecipeAction(r) for r in recipesThatWillMakeSomethingNeeded]
        elif len(recipesThatWillHelpARecipeRun)  !=0:
            actions=   [ExecuteRecipeAction(r) for r in recipesThatWillHelpARecipeRun]
        else:
            actions=list()

        for action in actions:
            assert FulfillmentPath([action]).canBeSuccessfullyAppliedTo(factory)
        return actions


class FulfillmentPath:
    def __init__(self,actionsInOrderOfExecuiton):
        self.actionsInOrderOfExecuiton = actionsInOrderOfExecuiton

    @classmethod
    def fulfillmentPaths(cls,order,factory):
        fulfillmentPaths=list()
        if order.required.numberOfItems()==0:
            return fulfillmentPaths
        firstActions = order.allFirstActions(factory)  # maybe we could  avoid deliver actions
        for action in firstActions:
            subPaths = cls.fulfillmentPaths(action.orderAfterAction(order),action.factoryAfterAction(factory))
            if len(subPaths)==0 and action.delivers.numberOfItems() > 0:
                newPath = FulfillmentPath([action])
                if newPath.satisfiesOrder(order):
                    if(not newPath.equivalentForIntialStateIsAlreadyPresentIn(fulfillmentPaths,factory))  :  #an optimization only add non equivalent paths
                        fulfillmentPaths.append(newPath)

            for subPath in subPaths:
                newPath = subPath.withPriorAction(action)
                if newPath.satisfiesOrder(order):
                    if(not newPath.equivalentForIntialStateIsAlreadyPresentIn(fulfillmentPaths,factory))  :  #an optimization only add non equivalent paths
                        fulfillmentPaths.append(newPath)
        return fulfillmentPaths



    def __eq__(self, other):
        if id(self)==id(other):
            return True
        elif type(other) is type(self):
            return vars(self).items() == vars(other).items()
        else:
            return False

    def __hash__(self):
        return hash(vars(self).items())

    def __str__(self):
        return "FP("+ ",".join([str(a) for a in self.actionsInOrderOfExecuiton])+")"

    def withPriorAction(self,action):
        return FulfillmentPath( [action] +self.actionsInOrderOfExecuiton )

    def withExtension(self,action):
        return FulfillmentPath(self.actionsInOrderOfExecuiton + [action])

    def equivalentForIntialStateIsAlreadyPresentIn(self,fulfillmentPaths,initalFactory):
        for p in fulfillmentPaths:
            if self.isEquivalentForIntialState(p,initalFactory) :
                return True
        return False

    def isEquivalentForIntialState(self,other,initalFactory):
        assert self.canBeSuccessfullyAppliedTo(initalFactory)
        assert other.canBeSuccessfullyAppliedTo(initalFactory)
        return self.deliveryAndFactoryAfterFulfilmentOrNoneNone(initalFactory) == other.deliveryAndFactoryAfterFulfilmentOrNoneNone(initalFactory)

    def canBeSuccessfullyAppliedTo(self,factory):
        (d,f) = self.deliveryAndFactoryAfterFulfilmentOrNoneNone(factory)
        return f is not None

    def deliveryAndFactoryAfterFulfilmentOrNoneNone(self,factory):
        f = factory
        delivery = ItemTypeQuantities()
        for action in self.actionsInOrderOfExecuiton:
            (newDelivery,f) = action.deliveryAndFactoryAfterAction(f)
            if(newDelivery is None):
                return (None,None)
            delivery=delivery.plus(newDelivery)
        assert delivery==self.delivers() # just a check
        return (delivery,f)

    def delivers(self):
        sum = ItemTypeQuantities()
        for a in self.actionsInOrderOfExecuiton:
            sum = sum.plus(a.delivers)
        return sum

    def satisfiesOrder(self,order):
        if(self.delivers().numberOfItems()==0):
            return False
        elif self.delivers() == order.required or order.allowPartialFulfillment:
            return True
        else:
            return False

class Action:

    def __eq__(self, other):
        if id(self)==id(other):
            return True
        elif type(other) is type(self):
            return vars(self).items() == vars(other).items()
        else:
            return False

    def __hash__(self):
        return hash(vars(self).items())


class DeliverAction(Action):
    def __init__(self,itemTypeToDeliver):
        self.delivers = ItemTypeQuantities({itemTypeToDeliver:1})

    def __str__(self):
        return "DA("+ str(self.delivers)+")"

    def deliveryAndFactoryAfterAction(self,factory) :
        newFactory =  Factory(factory.recipes, factory.inventory.minus(self.delivers))
        return (self.delivers , newFactory)

    def orderAfterAction(self,order):
        return Order(order.required.minus(ItemTypeQuantities(self.delivers)), order.allowPartialFulfillment)

    def factoryAfterAction(self,factory):
        newInventory=factory.inventory.minus(self.delivers)
        return Factory(factory.recipes, newInventory)


class ExecuteRecipeAction(Action):
    def __init__(self,recipeToExecute):
        self.recipeToExecute = recipeToExecute
        self.delivers=ItemTypeQuantities()

    def __str__(self):
        return "RA("+ str(self.recipeToExecute)+")"

    def deliveryAndFactoryAfterAction(self,factory) :
        newInventory=factory.inventory.minus(self.recipeToExecute.consumes).plus(self.recipeToExecute.produces)
        newFactory =  Factory(factory.recipes, newInventory)
        return (ItemTypeQuantities() , newFactory)

    def orderAfterAction(self,order):
        return order

    def factoryAfterAction(self,factory):
        (d,f)=self.deliveryAndFactoryAfterAction(factory)
        return f

def jsonObjFromString(jsonString):
    return  json.loads(jsonString)


def jsonObjFromFilePath(filePath):
    with open(filePath, 'r') as json_file:
        return  json.load(json_file)



def defaultInventory():
    jsonString="""
    {
    "iron_plate": 40, "iron_gear": 5, "copper_plate": 20, "copper_cable": 10, "lubricant": 100
    }   
    """
    return ItemTypeQuantities.fromJsonObj(jsonObj=jsonObjFromString(jsonString))

def defaultRecipies():
    jsonString = """
    {
"recipe_gear": {
"title": "Gear", "time": 0.5, "consumes": {
"iron_plate": 2 },
"produces": { "iron_gear": 1
} },
"recipe_pipe": { "title": "Pipe", "time": 0.5, "consumes": {
"iron_plate": 1 },
"produces": { "pipe": 1
} },
"recipe_cables": {
"title": "Copper Cable (2x)", "time": 0.5,
"consumes": {
"copper_plate": 1 },
"produces": { "copper_cable": 2
} },
"recipe_steel": { "title": "Steel Plate", "time": 16.0, "consumes": {
"iron_plate": 5 },
"produces": { "steel_plate": 1
} },
"recipe_circuit": {
"title": "Electric Circuit", "time": 1.5,
"consumes": {
"iron_plate": 1,
"copper_cable": 3 },
"produces": { "electric_circuit": 1
}
}, "recipe_engine_block": {
"title": "Engine Block", "time": 10.0, "consumes": {
"steel_plate": 1, "iron_gear": 1, "pipe": 2
}, "produces": {
"engine_block": 1 }
}, "recipe_elec_engine": {
"title": "Electric Engine", "time": 10.0,
"consumes": {
"electric_circuit": 2, "engine_block": 1, "lubricant": 15
}, "produces": {
"electric_engine": 1 }
} }
    """
    return  Recipe.recipesfromJsonObj(jsonObjFromString(jsonString))

def defaultOrders():
    return Order.fromStrings(["3x electric_engine","5x electric_circuit", "3x electric_engine"])

def testDefault():
    run()
    print("testDefault succeeded")

def testJustFindIt():
    oneA = ItemTypeQuantities({"a":1} )
    factory=Factory(inventory=oneA,recipes=list())

    paths = factory.bestFulfillmentPathForEachOrderInTurn([Order(oneA,False)])
    assert paths[0] is not None
    (d,f)= factory.deliveryAndFactoryAfterFulfillmentOrNoneNoneIfCant(paths[0])
    assert d == oneA
    assert f.sizeOfInventory() ==0
    print("testJustFindIt succeeded")

def  testOneRecipe():
    oneA = ItemTypeQuantities({"a":1} )
    oneB = ItemTypeQuantities({"b":1} )
    recipe = Recipe("bToA","bToA",ItemTypeQuantities({"b":1} ),ItemTypeQuantities({"a":1} ),10)
    factory=Factory(inventory=oneB,recipes=[recipe])

    paths = factory.bestFulfillmentPathForEachOrderInTurn([Order(oneA,False)])
    assert paths[0] is not None
    (d,f)= factory.deliveryAndFactoryAfterFulfillmentOrNoneNoneIfCant(paths[0])
    assert d == oneA
    assert f.sizeOfInventory() ==0
    print("testOneRecipe succeeded")

def  testTwoRecipes():
    oneA = ItemTypeQuantities({"a":1} )
    oneB = ItemTypeQuantities({"b":1} )
    oneC = ItemTypeQuantities({"c":1} )
    recipe1 = Recipe("bToA","bToA",ItemTypeQuantities({"b":1} ),ItemTypeQuantities({"a":1} ),10)
    recipe2 = Recipe("cToB","cToB",ItemTypeQuantities({"c":1} ),ItemTypeQuantities({"b":1} ),10)
    factory=Factory(inventory=oneC,recipes=[recipe1,recipe2])

    paths = FulfillmentPath.fulfillmentPaths(Order(oneA,False),factory)
    assert len(paths) ==1
    (d,f)= factory.deliveryAndFactoryAfterFulfillmentOrNoneNoneIfCant(paths[0])
    assert d == oneA
    assert f.sizeOfInventory() ==0
    print("testTwoRecipes succeeded")

def  testCantFindASolution():
    oneA = ItemTypeQuantities({"a":1} )
    oneB = ItemTypeQuantities({"b":1} )
    oneC = ItemTypeQuantities({"c":1} )
    #recipe1 = Recipe("bToA","bToA",ItemTypeQuantities({"b":1} ),ItemTypeQuantities({"a":1} ),10)
    recipe2 = Recipe("cToB","cToB",ItemTypeQuantities({"c":1} ),ItemTypeQuantities({"b":1} ),10)
    factory=Factory(inventory=oneC,recipes=[recipe2])

    paths = FulfillmentPath.fulfillmentPaths(Order(oneA,False),factory)
    assert len(paths) ==0

    print("testCantFindASolution succeeded")

def  testPartialSolution():
    oneA = ItemTypeQuantities({"a":1} )
    oneB = ItemTypeQuantities({"b":1} )
    oneC = ItemTypeQuantities({"c":1} )
    AAB =  ItemTypeQuantities({"a":2, "b":1} )
    ABB =  ItemTypeQuantities({"a":1, "b":2} )

    recipe1 = Recipe("bToA","bToA",ItemTypeQuantities({"b":1} ),ItemTypeQuantities({"a":1} ),10)
    recipe2 = Recipe("cToB","cToB",ItemTypeQuantities({"c":1} ),ItemTypeQuantities({"b":1} ),10)

    factory=Factory(inventory=AAB,recipes=[recipe1])
    order =  Order(ABB,True)

    paths = FulfillmentPath.fulfillmentPaths(order,factory)
    assert len(paths) ==1
    (d0,f0) = paths[0].deliveryAndFactoryAfterFulfilmentOrNoneNone(factory)
    assert d0.numberOfItems() == 2
    assert f0.sizeOfInventory() == 1
    print("testPartialSolution succeeded")

def tests():
    testPartialSolution()
    #---
    testJustFindIt()
    testOneRecipe()
    testTwoRecipes()
    testCantFindASolution()
    testPartialSolution()
    testDefault()

def run(args=None):
    inventory =  defaultInventory()
    recipes =  defaultRecipies()
    orders =  defaultOrders()
    if  args is not None and args.inv is not None:
        inventory = ItemTypeQuantities.fromJsonObj(jsonObjFromFilePath(args.inv))
    if  args is not None and args.recipes is not None:
        recipes = Recipe.recipesfromJsonObj(jsonObjFromFilePath(args.recipes))
    if  args is not None and args.orders is not None:
        orders = [Order.fromStrings(args.orders)]
    factory=Factory(inventory=inventory,recipes=recipes )
    paths = factory.bestFulfillmentPathForEachOrderInTurn(orders)
    deliveries = [factory.excutePath(p) for p in paths]
    for p in paths:
        p.printExecution()



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='run tests')
    parser.add_argument('--inv', nargs=2 ,default=None, help='inventory json file path')
    parser.add_argument('--recipes', nargs=2 ,default=None, help='recipies json file path')
    parser.add_argument('--orders', nargs='*' , default=None,help='orders note orders must be quoted')
    args = parser.parse_args()
    if args.test:
        tests()
    else:
        run(args)
