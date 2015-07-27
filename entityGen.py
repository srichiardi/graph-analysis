import csv


class Entity:
    __instances = {}
    def __init__(self, entType, entName, attrTypes=[]):
        self.type = entType
        self.name = entName
        self.group = None
        self.attributes = {}
        for item in attrTypes:
            self.attributes[item] = []
        # adding entity to the collection
        try:
            Entity.__instances[self.type][self.name] = self
        except KeyError:
            Entity.__instances[self.type] = { self.name : self}
        

    def joinGroup(self, alienEntity=None):
        # 2 different groups competing
        if self.group and alienEntity.group and (self.group.name != alienEntity.group.name):
            # negotiate which group to choose and move the members
            # local group wins
            if self.group.size >= alienEntity.group.size:
                self.group.annexGroup(alienEntity.group)
            # alien group wins
            else:
                alienEntity.group.annexGroup(self.group)
        # assigning other group if no own group is set
        elif not self.group and alienEntity.group:
            self.group = alienEntity.group
            self.group.addMember(self)
        # assigning his own new group if both local and alien groups are none
        elif not self.group and not alienEntity.group:
            self.group = Group()
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
    

    def linkTo(self, attribute):
        # adding attribute value to self entity
        if attribute.name not in self.attributes[attribute.type]:
            self.attributes[attribute.type].append(attribute.name)
            # and adding self entity to attribute entity
            attribute.attributes[self.type].append(self.name)
            
        # transfer group to attribute here?
        attribute.joinGroup(self)
            
    
    def nextNodes(self):
        # find entities corresponding to attributes and return a list of them 
        nodesList = []
        for attrType in self.attributes.keys():
            for attrID in self.attributes[attrType]:
                nextNode = Entity.__instances[attrType][attrID]
                nodeList.append(nextNode)

        return nodesList
    
    
    @classmethod
    def getEntity(cls, type, name, attrTypes):
        try:
            instance = cls.__instances[type][name]
        except KeyError:
            instance = cls(type, name, attrTypes)
            
        return instance
        


class Group:
    groupCount = 0
    def __init__(self):
        groupCount += 1
        self.members = []
        self.name = "G%d" % groupCount
        self.size = 0


    def addMember(self, newMember):
        if newMember not in self.members:
            self.members.append(member)
            self.size += 1


    def annexGroup(self, otherGroup):
        # transfer members from one group to another
        # and update members' group membership
        for member in otherGroup.members:
            self.addMember(member)
            member.group = self
        # remove empty group
        del otherGroup



## loading entities from CSV file
def loadEntities(fileName):
    fileToRead = open(fileName, "rb")
    csvReader = csv.reader(fileToRead, restval='', delimiter=',', dialect='excel',
                           quotechar='"')
    # fetch headers
    headers = csvReader.next()
    mainEntType = headers[0]
    attribTypes = headers[1:]
    
    for line in csvReader:
        # retrieve one that already exists
        # or create new main entity if not already existing
        mainEnt = Entity.getEntity(mainEntType, line[0], attribTypes)
        # create new or confirm current group
        # only main entities create groups, attributes only receive them and transfer them
        mainEnt.joinGroup()
        
        for idx, attrType in enumerate(attributes):
            colNr = idx + 1
            attribute = Entity.getEntity(attrType, line[colNr], [mainEntType])
            # add attributes to the entity
            # this is a two way operation, saving reference of both in each other
            mainEnt.linkTo(attribute)
                
    fileToRead.close()

# for entity in entities: main loop that takes every single main entity
# # entity.joinGroup() 
# # mainGroup = entity.group
# # for attriType in entity.attributes.keys():
# # # if not entity.attribute.checked:
# # # # for each entity linked to the attribute: skip only entity that is calling
# # # # # entity.joinGroup(mainGroup)
