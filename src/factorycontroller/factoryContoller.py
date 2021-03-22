
import json

class Recipe:
    def __init__(self,title,consumes,produces,elapsedSecondsToExecute):
        self.title = title
        self.consumes  =consumes
        self.produces  =produces
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
    def __init__(self):
        self.itemQuantityHeldByItemType = {}

    def addItemOfType(self,itemType):
        self.addNItemsOfType(itemType,1)

    def addNItemsOfType(self,itemType,n):
        self.itemQuantityHeldByItemTyped[itemType]= self.itemQuantityHeldByItemTyped.get(itemType,0) +n

    def quantityOfItemType(self,itemType):
         self.itemQuantityHeldByItemTyped.get(itemType,0)

    def fromQuantiityByTypeNameDict(self,quantityByTypeNameDict):        # Yes I know that ItemTypeQuantities is almost exactly this
         assert self is None #  ensure used as a simple instance creation method
         newOne = ItemTypeQuantities()
         for (name,quantity) in  quantityByTypeNameDict.items():
             newOne.addNItemsOfType(ItemType(name),quantity)
         newOne



class ItemType:
    def __init__(self,name):
        self.name=name

class Factory:

    def __init__(self,recipes,inventory):
        self.recipes=recipes
        self.inventory= inventory

    def executeOrder(self, order):
        order.required.


    def executeOrdersInOrder(self,orders):
        [o.executeOrder for o in  orders]


class OrderRequestingItems:
    def __init__(self,required,allowPartialFullFillment):
        self.required = required
        self.allowPartialFullFillment = True
