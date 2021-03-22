
# This alogotithm copes with the possibliity of more than one one to construct the build of an item
#i do make too many factories but that was the cost of trying all paths to fulfill  orders
# it is a bit of a mish mash of mutable and immutable - but the method names are always indicative
# orders may be muych more complicted than just an order for a single thing and they may be fully or partially delivered
#orders may optionally be place back in to the inventory this is the default  (but this is strange)

# the example run onlt made 4 

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

    def missingItemTypesThatPreventExecutionAgainstInventory(self,inventory):
        return self.consumes.itemTypesNotSubsumedBy(inventory)

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


    def recipesThatCANTExecuteThatCanProduceItemsFrom(self,itemTypes):
        return [r for r in self.recipes if (not r.canExecuteWithInventory(self.inventory)) and r.producesOneOf(set(itemTypes))]


    def missingItemTypesThatDirectlyPreventTheseItemTypesBeingProduced(self,itemTypes):
        recipesWeWouldWantToRun =  self.recipesThatCANTExecuteThatCanProduceItemsFrom(itemTypes)
        listOFListOfItemTypes = [r.missingItemTypesThatPreventExecutionAgainstInventory(self.inventory) for r in recipesWeWouldWantToRun]
        itemTypes = [item for sublist in listOFListOfItemTypes for item in sublist]
        return set(itemTypes)
        


    def itemTypesThatAreMisingAndPreventRecipesFormExecuting(self):
        listOFListOfItemTypes = [r.missingItemTypesThatPreventExecutionAgainstInventory(self.inventory) for r in self.recipes]
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

    def excutePathReturningDeliveryOrNone_DONTUSEIT(self,fulfillmentPath):  # a hack to make factories  change
        delivery = ItemTypeQuantities()
        (delivery,newFactory) = fulfillmentPath.deliveryAndFactoryAfterFulfilmentOrNoneNone(self)
        self.inventory=copy.deepcopy(newFactory.inventory)
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
        equalBest =  FulfillmentPath.bestFulfillmentPathsByOverAllRating(paths,self)
        if len(equalBest) >1:
            print("hi chad 1 len(equalBest)=" + str(len(equalBest)))
        return equalBest[0]
       

class Order:
    def __init__(self,required,allowPartialFulfillment,returnToInventory=False):
        self.required = required
        self.allowPartialFulfillment = allowPartialFulfillment
        self.returnToInventory=returnToInventory

    @classmethod
    def fromString(cls, orderString):          
        amountXType=orderString.split()
        assert len(amountXType) == 2  or (len(amountXType) == 3 and (amountXType[2] == "RTN" or amountXType[2]=="RMV"))
        amount= int(amountXType[0].lower().replace("x",""))
        typeName=   amountXType[1]
        returnToInv = not (len(amountXType) == 3  and amountXType[2] == "RMV")

        return cls(ItemTypeQuantities({typeName:amount}),True, returnToInv)

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

    def isOrderStatifiedByDelivery(self,delivery):
        return self.missingAfterDelivery(delivery).numberOfItems()==0

    def missingAfterDelivery(self,delivery):
        return self.required.minus(delivery)

    def allFirstActions(self,factory):  # factory allows us to limit the possible first actions with out just tryng them ll
        # always deliver if possible
        # run any recipe that mught produce a new thing to deliver
        # run any recipe that creates items that the invetory does not have that prevets a recipe for runing
        # so either there is a  recipe that can run that will produce and item or there are items that need to be built
            # so attempting to run a reciept that might help another recipy run is a good thing
            # all recipes that can run but dont help an un runnable recipe dont help
        deliveryActions =  [DeliverAction(itemType) for itemType in self.required.itemTypesPresent() if factory.hasItemTypeInInventory(itemType)]
        if len(deliveryActions)!=0:
            return [deliveryActions[0]]

        # recipesThatWillMakeSomethingNeeded = factory.recipesThatCanExecuteThatCanProduceItemsFrom(self.required.itemTypesPresent())
        # if len(recipesThatWillMakeSomethingNeeded)  !=0:
        #    return [[ExecuteRecipeAction(r) for r in recipesThatWillMakeSomethingNeeded][0]]

        usefulItemTypesToCreate =   set(self.required.itemTypesPresent())

        # just return one to get a result
        while True:
            recipesThatWillMakeSomethingNeeded=factory.recipesThatCanExecuteThatCanProduceItemsFrom(usefulItemTypesToCreate)
            if len(recipesThatWillMakeSomethingNeeded)  !=0:
                return [ExecuteRecipeAction(r) for r in recipesThatWillMakeSomethingNeeded]
            missingItemTypesForRecipes = factory.missingItemTypesThatDirectlyPreventTheseItemTypesBeingProduced(usefulItemTypesToCreate)
            if missingItemTypesForRecipes.issubset(usefulItemTypesToCreate) :
                return list()
            usefulItemTypesToCreate= usefulItemTypesToCreate.union(missingItemTypesForRecipes)
        #
        # recipesThatWillHelpARecipeRun  = factory.recipesThatCanExecuteThatCanProduceItemsFrom(factory.itemTypesThatAreMisingAndPreventRecipesFormExecuting())
        #
        # if len(recipesThatWillHelpARecipeRun)  !=0:
        #     return [ExecuteRecipeAction(r) for r in recipesThatWillHelpARecipeRun]
        #


        # for action in actions:
        #     assert FulfillmentPath([action]).canBeSuccessfullyAppliedTo(factory)
        # return actions
        return  list()

class FulfillmentPath:
    def __init__(self,actionsInOrderOfExecuiton,order):
        self.actionsInOrderOfExecuiton = actionsInOrderOfExecuiton
        self.order=order

    @classmethod
    def fulfillmentPaths(cls,order,factory):
        fulfillmentPaths=list()
        if order.required.numberOfItems()==0:
            return fulfillmentPaths
        firstActions = order.allFirstActions(factory)  # maybe we could  avoid deliver actions
        for action in firstActions:
            subPaths = cls.fulfillmentPaths(action.orderAfterAction(order),action.factoryAfterAction(factory))
            if len(subPaths)==0 and action.delivers.numberOfItems() > 0:
                newPath = FulfillmentPath([action],order)
                if newPath.satisfiesOrder(order):
                    if(not newPath.equivalentForIntialStateIsAlreadyPresentIn(fulfillmentPaths,factory))  :  #an optimization only add non equivalent paths
                        fulfillmentPaths.append(newPath)

            for subPath in subPaths:
                newPath = subPath.withPriorAction(action,order)
                if newPath.satisfiesOrder(order):
                    if(not newPath.equivalentForIntialStateIsAlreadyPresentIn(fulfillmentPaths,factory))  :  #an optimization only add non equivalent paths
                        fulfillmentPaths.append(newPath)
        return cls.bestFulfillmentPathsByOverAllRating(fulfillmentPaths,factory)

    @classmethod
    def bestFulfillmentPathsByDeliveredRating(cls,paths):
        if len(paths)==0:
            return paths
        maxRating = max([p.deliveredRating() for p in paths])
        return [p for p in paths if p.deliveredRating()==maxRating]

    @classmethod
    def bestFulfillmentPathsByOverAllRating(cls,paths,initialFactory):
        if len(paths)<=1:
            return paths
        maxRating = max([p.overAllRatingConsideringFinalInventory(initialFactory) for p in paths])
        if abs(maxRating-0)<1e-5 :
            return paths
        return [p for p in paths if (abs(p.overAllRatingConsideringFinalInventory(initialFactory)-maxRating)/maxRating) < 1e-5]


    def deliveredRating(self):
        return self.delivers().numberOfItems()

    def  overAllRatingConsideringFinalInventory(self,initialFactory):
        (d,f)=initialFactory.deliveryAndFactoryAfterFulfillmentOrNoneNoneIfCant(self)
        return d.numberOfItems() + f.sizeOfInventory()/(10*initialFactory.sizeOfInventory() ) #*2 incase we create more

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

    def withPriorAction(self,action,order):
        return FulfillmentPath( [action] +self.actionsInOrderOfExecuiton,order )

    def withExtension(self,action,order):
        return FulfillmentPath(self.actionsInOrderOfExecuiton + [action],order)

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
        assert delivery==self.delivers() # just a check ]
        if self.order.returnToInventory:
            f= Factory(f.recipes,f.inventory.plus(delivery))
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

    def printExecution(self):
        for i in range(0,len(self.actionsInOrderOfExecuiton)):
            print(self.actionsInOrderOfExecuiton[i].executionPrintString(self.actionsInOrderOfExecuiton[0:i]))


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
        self.itemTypeToDeliver=itemTypeToDeliver
        self.delivers = ItemTypeQuantities({itemTypeToDeliver:1})

    def __str__(self):
        return "DA("+ str(self.delivers)+")"

    def deliveryAndFactoryAfterAction(self,factory) :
        newFactory =  Factory(factory.recipes, factory.inventory.minus(self.delivers))
        return (self.delivers , newFactory)

    def orderAfterAction(self,order):
        return Order(order.required.minus(ItemTypeQuantities(self.delivers)), order.allowPartialFulfillment,False)

    def factoryAfterAction(self,factory):
        newInventory=factory.inventory.minus(self.delivers)
        return Factory(factory.recipes, newInventory)

    def timeToExecute(self):
        return 0

    def executionPrintString(self,priorActions):
        elapsedTime = sum([a.timeToExecute() for a in priorActions ],0)
        return "Delivered a " + self.itemTypeToDeliver.name + " after " + str(elapsedTime) + "s"


class ExecuteRecipeAction(Action):
    def __init__(self,recipeToExecute):
        self.recipeToExecute = recipeToExecute
        self.delivers=ItemTypeQuantities()

    def __str__(self):
        return "RA("+ str(self.recipeToExecute)+")"

    def timeToExecute(self):
        return self.recipeToExecute.elapsedSecondsToExecute

    def deliveryAndFactoryAfterAction(self,factory) :
        newInventory=factory.inventory.minus(self.recipeToExecute.consumes).plus(self.recipeToExecute.produces)
        newFactory =  Factory(factory.recipes, newInventory)
        return (ItemTypeQuantities() , newFactory)

    def orderAfterAction(self,order):
        return Order(order.required,order.allowPartialFulfillment,False)

    def factoryAfterAction(self,factory):
        (d,f)=self.deliveryAndFactoryAfterAction(factory)
        return f

    def executionPrintString(self,priorActions):
        return "  executing recipe " + self.recipeToExecute.name + " takes " + str(self.timeToExecute())+ "s building " +  ",".join([str(self.recipeToExecute.produces.quantityOfItemType(itemType))+" X "+ itemType.name for itemType in self.recipeToExecute.produces.itemTypesPresent()])

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
    testDefault()
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
    #deliveries = [factory.excutePathReturningDeliveryOrNone(p) if p is not None else None for p in paths ]
    for p in paths:
        if p is not None:
            print("")
            p.printExecution()
            print("")

    inventoryAndDeliveryAfterEachOrder = list()
    f = factory
    for p in paths :
        if p is not None:
            (d,f) = p.deliveryAndFactoryAfterFulfilmentOrNoneNone(f)
            inventoryAndDeliveryAfterEachOrder.append((d,f.inventory) )
        else:
            inventoryAndDeliveryAfterEachOrder.append(None)

    matchedOrders =  [(orders[i],inventoryAndDeliveryAfterEachOrder[i][0],inventoryAndDeliveryAfterEachOrder[i][1]) for i in range(0,len(orders)) ]
    print(" inv before orders: "+ str(factory.inventory) )
    for (o,d,inv) in matchedOrders:
        if d is  None:
            print("Order Unfulfilled  " + str(o.required) )
        elif o.isOrderStatifiedByDelivery(d):
            print("Satisfied order " + str(o.required) )
            print(" inv after order: "+ str(inv) )
        else:
            print("Order partially filled  " ) 
            print("  received:" + str(d))
            print("  missing: " + str(o.missingAfterDelivery(d)) )
            print(" inv after order: "+ str(inv) )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='run tests')
    parser.add_argument('--inv', nargs=2 ,default=None, help='inventory json file path')
    parser.add_argument('--recipes', nargs=2 ,default=None, help='recipies json file path')
    parser.add_argument('--orders', nargs='*' , default=None,help='orders note orders must be quoted of form <n>x <itemname> [RTN|RMV]. Note RTN means return order to inventory RMV means remove from inventory, RTN is the default')
    args = parser.parse_args()
    if args.test:
        tests()
    else:
        run(args)
