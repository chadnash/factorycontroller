
# This alogotithm copes with the possibliity of more than one one to construct the build of an item
#i do make too many factories but that was the cost of trying all paths to fulfill  orders
# it is a bit of a mish mash of mutable and immutable - but the method names are always indicative 


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
    def __deepcopy__(self,memo):
        #Recipies are imputable so copy can be itself
        return self

class  Recipes:
    def __init__(self,recipies):
        self.recipies=recipies

    @classmethod
    def fromJsonObj(cls,jsonObj):
        assert  isinstance(jsonObj,dict)
        recipes = [ ]
        return cls([Recipe.fromJsonObjAndName(key,jsonObj[key]) for key in jsonObj])

    def __deepcopy__(self,memo):
        #Recipies are imputable so copy can be itself
        return self

class ItemTypeQuantities:
    def __init__(self, quantByItems = None):
        if(quantByItems is None):
            self.itemQuantityHeldByItemType = {}
        else:
            self.itemQuantityHeldByItemType =copy.deepcopy(quantByItems)  # ensure I am immutable
        for  k in self.itemQuantityHeldByItemType:
            assert self.itemQuantityHeldByItemType[k]>=0
            
    @classmethod
    def fromJsonObj(cls,jsonObj):
        return cls.fromQuantityByTypeNameDict(jsonObj)
        
    @classmethod
    def fromQuantityByTypeNameDict(cls,quantityByTypeNameDict):        # Yes I know there may be no value in wrapping strings in itemtypes
        quantByItemType = {}
        for (name,quantity) in  quantityByTypeNameDict.items():
            quantByItemType[ItemType(name)]=quantity
        return cls(quantByItemType)


    def quantityOfItemType(self,itemType):
        return self.itemQuantityHeldByItemTyped.get(itemType,0)

    def withOneRemoved(self,itemType):
        quantByItemType = self.itemQuantityHeldByItemType.dee
        assert quantByItemType.get(itemType,None) is not None
        quantByItemType[itemType]= quantByItemType[itemType] -1
        return ItemTypeQuantities(quantByItemType)

    def plus(self,other):
        keys = set()
        keys.addAll(self.itemQuantityHeldByItemType.keys)
        keys.addAll(other.itemQuantityHeldByItemType.keys)

        return ItemTypeQuantities({key: self.quantityOfItemType(key)+other.quantityOfItemType(key) for key in keys })

    def minus(self,other):
        keys = set()
        keys.addAll(self.itemQuantityHeldByItemType.keys.copy)
        keys.addAll(other.itemQuantityHeldByItemType.keys.copy)

        return ItemTypeQuantities({key: self.quantityOfItemType(key)-other.quantityOfItemType(key) for key in keys })

    def __deepcopy__(self,memo):
        #ItemTypeQuantities are imputable so copy can be itself
        return self

class ItemType:
    def __init__(self,name):
        self.name=name
    def __deepcopy__(self,memo):
        #ItemType are imputable so copy can be itself
        self


class Factory:

    def __init__(self,recipes,inventory):
        self.recipes=recipes.deepCopy
        self.inventory= inventory.deepCopy

    def deliveryAndFactoryAfterFulfillmentOrNoneNoneIfCant(self,fulfillmentPath):
        f = self.copy
        delivery = f.excutePathReturnDeliveryOrNone(fulfillmentPath)
        return (delivery,f)
            
    def excutePathReturningDeliveryOrNone(self,fulfillmentPath):  # a hack to make factories  change
        delivery = ItemTypeQuantities()
        (delivery,newFactory) = fulfillmentPath.deliveryAndFactoryAfterFulfilmentOrNoneNone(self)
        self.inventory=newFactory.inventory.deepCopy
        return delivery



class Order:
    def __init__(self,required,allowPartialFulfillment):
        self.required = required
        self.allowPartialFulfillment = True



class FufillmentPath:
    def __init__(self,actionsInOrderOfExecuiton):
        self.actionsInOrderOfExecuiton = actionsInOrderOfExecuiton
    def fulfillmentPaths(self,order,factory):
        fulfillmentPaths=set()
        firstActions = order.allFirstActions(factory)  # maybe we could  avoid deliver actions
        for action in firstActions:
            subPaths = FufillmentPath.fulfillmentPaths(order.afterAction(action),factory.afterAction(action))
            for subPath in subPaths:
                newPath = subPath.followedBy(action)
                if(not newPath.equivalentForIntialStateIsAlreadyPresentIn(fulfillmentPaths))  :  #an optimization only add non equivalent paths
                    fulfillmentPaths.add(newPath)
        return fulfillmentPaths

    def equivalentForIntialStateIsAlreadyPresentIn(self,fulfillmentPaths,initalFactory):
       None

    def isEquivalentForIntialState(self,other,initalFactory):
        assert self.canBeSuccessfullyAppliedTo(initalFactory)
        assert other.canBeSuccessfullyAppliedTo(initalFactory)
        return self.delivered == other.delivered and initalFactory.afterFulfillmentOrNoneIfCant(self)==  initalFactory.afterFulfillmentOrNoneInCant(other)

    def canBeSuccessfullyAppliedTo(self,factory):
        (d,f) = self.deliveryAndFactoryAfterFulfilmentOrNoneNone(factory)
        return f is not None

    def deliveryAndFactoryAfterFulfilmentOrNoneNone(self,factory):
        f = factory
        delivery = ItemTypeQuantities
        for action in self.actionsInOrderOfExecuiton:
            (newDelivery,f) = action.deliveryAndFactoryAfterAction(f)
            if(newDelivery is None):
                return (None,None)
            delivery=delivery.plus(newDelivery)
        return (delivery,f)



class Action:
    None

class DeliverAction(Action):
    def __init__(self,itemTypeToDeliver):
        self.itemTypeToDeliver = itemTypeToDeliver

    def deliveryAndFactoryAfterAction(self,factory) :
        delivered = ItemTypeQuantities({self.addItemOfType:1})
        newFactory =  Factory(factory.recipes, factory.inventory.minus(delivered))
        return (delivered ,newFactory )


class ExecuteRecipeAction(Action):
    def __init__(self,recipeToExecute):
        self.recipeToExecute = recipeToExecute

    def deliveryAndFactoryAfterAction(self,factory) :
        newInventory=factory.inventory.minus(self.recipeToExecute.consumes).plus(self.recipeToExecute.produces)
        newFactory =  Factory(factory.recipes, newInventory)
        return (ItemTypeQuantities() , newFactory)

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
    return  Recipes.fromJsonObj(jsonObjFromString(jsonString))

def defaultOrders():
    return Order.fromStrings(["3x electric_engine","5x electric_circuit", "3x electric_engine"])

def test1():
    run()
    
def tests():
     test1()

def run(args=None):
    inventory =  defaultInventory()
    recipes =  defaultRecipies()
    orders =  defaultOrders()
    if  args is not None and args.inv is not None:
        inventory = ItemTypeQuantities.fromJsonObj(jsonObjFromFilePath(args.inv))
    if  args is not None and args.recipes is not None:
        recipes = Recipes.fromJsonObj(jsonObjFromFilePath(args.recipes))
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
          