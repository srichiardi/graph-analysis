import csv

# entity generator
class Entity:
    instances = {}
    def __init__(self, Type=entType, Id=eID, *args):
        self.type = entType
        self.group = None
        self.id = eID
        self.checked = False
        self.attributes = {}
        for arg in args:
            self.attributes[arg] = []
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

    def getDict(self):
        if self.group:
            groupName = self.group.name
        else:
            groupName = ""
        entityDict = {"ENTITY_TYPE" : self.type,
                      "ENTITY_ID" : self.id,
                      "ENTITY_GROUP" : groupName}
        return entityDict

    def addAttribute(self, attrType, attrValue):
        if attrValue not in self.attributes[attrType]:
            self.attributes[attrType].append(attrValue)


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

## loading entities
fileToRead = open("./myfile.csv", "rb")
mainEntity = "ebay_acct"
attributes = ("iban")
for line in fileToRead:
    # create new main entity if not already existing
    if line[mainEntity] not in Entity.instances[mainEntity].keys():
        entity = Entity(Type=mainEntity, Id=line[mainEntity], attributes)
    else:
        # retrive entity from class collection if already existing
        Id = line[mainEntity]
        entity = Entity.instances[mainEntity][Id]
    
    for attribute in attributes:
        # add attributes to the entity
        entity.addAttribute(attribute, line[attribute])
        
        # create an entity with each attribute
        if line[attribute] not in Entity.instances[attribute].keys():
            attrEntity = Entity(Type=attribute, Id=line[attribute], mainEntity)
        else:
            Id = line[attribute]
            attrEntity = Entity.instances[attribute][Id]
        # add main entities in attribute that are not already present
        # attribute entities link to main entities only, not between each other
        attrEntity.addAttribute(mainEntity, line[mainEntity])
        

fileToRead.close()
