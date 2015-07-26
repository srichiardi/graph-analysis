import csv

# entity generator
class Entity:
    instances = {}
    def __init__(self, Type=entType, Id=eID, *args):
        # if entity type and id already in instances, retrieve instance
        if eID in Entity.instances[entType].keys():
            self = Entity.instances[entType][eID]
        
        # else create one entity from scratch
        else:
            self.type = entType
            self.group = None
            self.id = eID
            self.checked = False
            self.attributes = {}
            for arg in args:
                self.attributes[arg] = []
            # adding entity to the collection
            if entType not in Entity.instances.keys():
                Entity.instances[entType] = { self.id : self }
            else:
                Entity.instances[entType][self.id] = self

    def joinGroup(self, newGroup=None):
        # 2 groups competing
        if self.group and newGroup:
            # negotiate which group to choose and move the members
            if self.group.size >= newGroup.size:
                self.group.annexGroup(newGroup)
            else:
                newGroup.annexGroup(self.group)
        # assigning other group if no own group is set
        elif not self.group and newGroup:
            self.group = newGroup
            newGroup.addMember(self)
        # assigning his own new group
        elif not self.group and not newGroup:
            self.group = Group(Type=self.type)
            self.group.addMember(self)
        # if the group was already set by another entity, then do nothing

    def getDict(self):
        if self.group:
            groupName = self.group.name
        else:
            groupName = ""
        entityDict = {self.type : self.id,
                      "GROUP" : groupName}
        return entityDict

    def linkAttribute(self, attrType, attrValue):
        # adding both attribute value to self entity
        # and adding self entity to attribute entity
        if attrValue not in self.attributes[attrType]:
            self.attributes[attrType].append(attrValue)
            attribute = Entity(attrType, attrValue, self.type)
            # !!! make sure there are no duplicates!!!!
            attribute.attributes[self.type].append(self.id)
    
    def nextNodes(self):
        # find entities corresponding to attributes and return a list of them 
        nodesList = []
        for attrType in self.attributes.keys():
            for attrID in self.attributes[attrType]:
                nextNode = Entity.instances[attrType][attrID]
                nodeList.append(nextNode)

        return nodesList


class Group:
    groupCount = 0
    def __init__(self, Type=groupType):
        groupCount += 1
        self.type = groupType
        self.members = []
        self.name = "G%d" % groupCount
        self.size = 0

    def addMember(self, newMember):
        if newMember not in self.members:
            self.members.append(member)
            self.size += 1

    def annexGroup(self, otherGroup):
        self.members.extend(otherGroup)
        for member in otherGroup.members:
            member.group = self
        del otherGroup

## loading entities from CSV file
def loadEntities(fileName):
    fileToRead = open(fileName, "rb")
    csvReader = csv.DictReader(fileToRead)
    mainEntity = "ebay_acct"
    attributes = ("iban")
    for line in fileToRead:
        # create new main entity if not already existing
        # or retrieve one that already exhists
        entity = Entity(Type=mainEntity, Id=line[mainEntity], attributes)
        
        for attrType in attributes:
            # add attributes to the entity
            # this is a two way operation, saving reference of both in each other
            entity.linkAttribute(attrType, line[attribute])
                
    fileToRead.close()

# for entity in entities: main loop that takes every single main entity
# # entity.joinGroup() 
# # mainGroup = entity.group
# # for attriType in entity.attributes.keys():
# # # if not entity.attribute.checked:
# # # # for each entity linked to the attribute: skip only entity that is calling
# # # # # entity.joinGroup(mainGroup)