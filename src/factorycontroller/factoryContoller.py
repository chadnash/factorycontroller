
import json

#i do make too many factories but that was the cost of tring all paths

class Recipe:
    def __init__(self,title,consumes,produces,elapsedSecondsToExecute):
        self.title = title
        self.consumes  =consumes.copy
        self.produces  =produces.copy
        self.elapsedSecondsToExecute =elapsedSecondsToExecute
    def fromJsonDict(self,jsonDict):
        assert self is None #  ensure used as a simple instance creation method
        Recipe(jsonDict["title"],
               ItemTypeQuantities.fromQuantiityByTypeNameDict(jsonDict["consumes"]),
               ItemTypeQuantities.fromQuantiityByTypeNameDict(jsonDict["produces"]),
               jsonDict["time"])

class  Recipes:
    def __init__(self,recipies):
        self.recipies=recipies

    def fromJsonList(self,jsonList):
        assert self is None #  ensure used as a simple instance creation method
        Recipes([Recipe.fromJsonDict(recipeDict) for recipeDict in jsonList])


class ItemTypeQuantities:
    def __init__(self, quantByItems = None):
        if(quantByItems is None):
            self.itemQuantityHeldByItemType = {}
        else:
            self.itemQuantityHeldByItemType =quantByItems.copy
        for  k in self.itemQuantityHeldByItemType:
            assert self.itemQuantityHeldByItemType[k]<0

    def addItemOfType(self,itemType):
        self.addNItemsOfType(itemType,1)

    def addNItemsOfType(self,itemType,n):
        self.itemQuantityHeldByItemTyped[itemType]= self.itemQuantityHeldByItemTyped.get(itemType,0) +n

    def quantityOfItemType(self,itemType):
         self.itemQuantityHeldByItemTyped.get(itemType,0)

    @classmethod
    def fromQuantityByTypeNameDict(cls,quantityByTypeNameDict):        # Yes I know there may be no value in wrapping strings in itemtypes
         quantByItemType = {}
         for (name,quantity) in  quantityByTypeNameDict.items():
             quantByItemType[ItemType(name)],quantity
         cls(quantByItemType)

    def withOneRemoved(self,itemType):
        quantByItemType = self.itemQuantityHeldByItemType.copy
        assert quantByItemType.get(itemType,None) is not None
        quantByItemType[itemType]= quantByItemType[itemType] -1
        ItemTypeQuantities(quantByItemType)

    def plus(self,other):
        keys = set()
        keys.addAll(self.itemQuantityHeldByItemType.keys.copy)
        keys.addAll(other.itemQuantityHeldByItemType.keys.copy)

        ItemTypeQuantities({key: self.quantityOfItemType(key)+other.quantityOfItemType(key) for key in keys })

    def minus(self,other):
        keys = set()
        keys.addAll(self.itemQuantityHeldByItemType.keys.copy)
        keys.addAll(other.itemQuantityHeldByItemType.keys.copy)

        ItemTypeQuantities({key: self.quantityOfItemType(key)-other.quantityOfItemType(key) for key in keys })



class ItemType:
    def __init__(self,name):
        self.name=name

class Factory:

    def __init__(self,recipes,inventory):
        self.recipes=recipes.copy
        self.inventory= inventory.copy

    def afterFullFillmentOrNoneIfCant(self,fullfillmentPath):
        for action in fullfillmentPath.actionsInOrderOfExecuiton

    def deliveryAndFactoryAfterAction(self,action):
        action.deliveryAndFactoryAfterAction(self)


class OrderRequestingItems:
    def __init__(self,required,allowPartialFullFillment):
        self.required = required
        self.allowPartialFullFillment = True



class FufillmentPath:
    def __init__(self,actionsInOrderOfExecuiton):
        self.recipiesInOrderOfExecuiton = actionsInOrderOfExecuiton
    def fullFillmentPaths(self,order,factory):
        fullFillmentPaths=set()
        firstActions = order.allFirstActions(factory)  # maybe we could  avoid deliver actions
        for action in firstActions:
            subPaths = FufillmentPath.fullFillmentPaths(order.afterAction(action),factory.afterAction(action))
            for subPath in subPaths:
                newPath = subPath.precededBy(action)
                if(not newPath.equivalentForIntialStateIsAlreadyPresentIn(fullFillmentPaths))  :  #an optimization only add non equivalent paths
                    fullFillmentPaths.add()
        fullFillmentPaths

    def equivalentForIntialStateIsAlreadyPresentIn(self,fullFillmentPaths,initalFactory):
        None

    def isEquivalentForIntialState(self,other,initalFactory):
        assert self.canBeSuccessfullyAppliedTo(initalFactory)
        assert other.canBeSuccessfullyAppliedTo(initalFactory)
        self.delivered == other.delivered and initalFactory.afterFullFillmentOrNoneIfCant(self)==  initalFactory.afterFullFillmentOrNoneInCant(other)

    def canBeSuccessfullyAppliedTo(self,factory):
        factory.afterFullFillmentOrNoneIfCant(self) is None

class Action:
    None

class DeliverAction(Action):
    def __init__(self,itemTypeToDeliver):
        self.itemTypeToDeliver = itemTypeToDeliver

    def deliveryAndFactoryAfterAction(self,factory) :
        delivered = ItemTypeQuantities()
        delivered.addItemOfType(self.itemTypeToDeliver)
        newFactory =  Factory(factory.recipes, factory.inventory.withOneRemoved(self.itemTypeToDeliver))
        (delivered ,newFactory )


class ExecuteRecipeAction(Action):
    def __init__(self,recipeToExecute):
        self.recipeToExecute = recipeToExecute

    def deliveryAndFactoryAfterAction(self,factory) :
        newInventory=factory.inventory.minus(self.recipeToExecute.consumes).plus(self.recipeToExecute.produces)
        newFactory =  Factory(factory.recipes, newInventory)
        (ItemTypeQuantities() , )

def test1():
    None

def tests():
     test1()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='run tests')
    parser.add_argument('--inv', nargs=2 ,default=None, help='inventory json file path')
    parser.add_argument('--recipes', nargs=2 ,default=None, help='recipies json file path')
    parser.add_argument('--orders', nargs='*' , help='orders')
    args = parser.parse_args()
    if args.test:
        tests()
    else:
        inventory =

    