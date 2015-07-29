from weakref import WeakValueDictionary
import csv
import sys


class Entity:
    __mainEntityType = ''
    __attributeTypes = []
    __groupType = 'GROUP'
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
        ''' 2 different groups competing '''
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

    
    def getPrintableDicts(self):
        if self.group:
            groupName = self.group.name
        else:
            groupName = ""
        
        dictList = []
        nextAttr = True
        
        while nextAttr == True:
            tempDict = {}
            nextAttr = False
            tempDict = { self.type : self.name,
                        Entity.__groupType : groupName }
            
            for key in self.attributes.keys():
                try:
                    value = self.attributes[key].pop()
                    nextAttr = True
                except IndexError:
                    value = ''
                finally:
                    tempDict[key] = value
                    
            if nextAttr:
                dictList.append(tempDict)
        
        return dictList
    

    def linkTo(self, attribute):
        ''' linking main entity to attribute entity '''
        if attribute.name not in self.attributes[attribute.type]:
            self.attributes[attribute.type].append(attribute.name)
            # and adding self entity to attribute entity
            attribute.attributes[self.type].append(self.name)
            
            # negotiate group with attribute
            attribute.joinGroup(self)
            
    
    def nextNodes(self):
        ''' finds entities directly linked to the current one and returns a list '''
        nodesList = []
        for attrType in self.attributes.keys():
            for attrID in self.attributes[attrType]:
                nextNode = Entity.__instances[attrType][attrID]
                nodeList.append(nextNode)

        return nodesList
    
    
    @classmethod
    def getEntity(cls, type, name, attrTypes):
        ''' method to check if an entity exists before creating one '''
        try:
            instance = cls.__instances[type][name]
        except KeyError:
            instance = cls(type, name, attrTypes)
            
        return instance
    
    
    @classmethod
    def importFromFile(cls, csvFileName):
        ''' take a CSV file as input, reads it and create main and attribute entities,
        groups and links in between '''
        fileToRead = open(csvFileName, "rb")
        csvReader = csv.reader(fileToRead, delimiter=',', dialect='excel',
                               quotechar='"')
        # fetch headers
        headers = csvReader.next()
        mainEntType = headers[0]
        attribTypes = headers[1:]
        
        # in case of second import, exit if main entity type doesn't match 
        if Entity.__mainEntityType != '' and Entity.__mainEntityType != mainEntType:
            fileToRead.close()
            sys.exit("Main Entity conflict: please double check the data being imported!")
        # or if first import, assign main entity type to class variable
        elif Entity.__mainEntityType == '':
            Entity.__mainEntityType = mainEntType
        
        # updating the class var attribute types with new types during first and later imports
        for attribType in attribTypes:
            if attribType not in Entity.__attributeTypes:
                Entity.__attributeTypes.append(attribType)
        
        for line in csvReader:
            # retrieve one that already exists
            # or create new main entity if not already existing
            mainEnt = Entity.getEntity(mainEntType, line[0], attribTypes)
            # only main entities create groups, attributes receive them and transfer them
            # if a GROUP header exists, assign it at import stage
            if Entity.__groupType in attribTypes:
                gIdx = attribTypes.index(Entity.__groupType) + 1
                importedGroup = Group.getGroupByName(line[gIdx])
                mainEnt.joinGroup(importedGroup)
            # create new or confirm current group
            # when no GROUP header is in the imported file
            else:
                mainEnt.joinGroup()
 
            for idx, attrType in enumerate(attributes):
                colNr = idx + 1
                attribute = Entity.getEntity(attrType, line[colNr], [mainEntType])
                # add attributes to the entity, and join same group
                mainEnt.linkTo(attribute)
                    
        fileToRead.close()
        
        
    @classmethod
    def printStats(cls):
        ''' providing information on all groups:
        nr of main entities, tot nr of groups, nr of groups with more than 50 main entities,
        nr of groups with less than 2 main entities (unlinked potentially linkable),
        attribute entities linked to many main entities (most popular)... '''
        pass
    
    
    @classmethod
    def exportToFile(cls, folderPath):
        ''' print main entities, relative attributes and groups they belong in CSV format. '''
        fileName = folderPath + "/entithon_export_%s.csv" % datetime.now().strftime("%Y%m%d_%H-%M-%S")
        csvFileToWrite = open(fileName, 'ab')
        
        fieldNames = [Entity.__mainEntityType]
        fieldNames.extend(Entity.__attributeTypes)
        fieldNames.append(Entity.__groupType)
        
        csvWriter = csv.DictWriter(csvFileToWrite, fieldNames, restval='', delimiter=',',
                                   extrasaction='ignore', dialect='excel', quotechar='"')
        csvWriter.writeheader()
        # iterate through main entities
        for entity in Entity.__instances[Entity.__mainEntityType].values():
            entityRecords = entity.getPrintableDicts()
            csvWriter.writerows(entityRecords)
            
        csvFileToWrite.close()


class Group:
    __groupCount = 0 # for naming purpose only
    __groupInstances = WeakValueDictionary()
    
    
    def __init__(self, name=None):
        __groupCount += 1
        self.members = []
        if name:
            self.name = name
        else:
            self.name = "G-%d" % __groupCount
        self.size = 0
        Group.__groupInstances[self.name] = self


    def addMember(self, newMember):
        ''' add new group member entities to the group list '''
        if newMember not in self.members:
            self.members.append(member)
            self.size += 1


    def annexGroup(self, otherGroup):
        ''' transfer members from one group to another and update members' group membership '''
        for member in otherGroup.members:
            self.addMember(member)
            member.group = self
        # remove empty group
        del otherGroup
        
    
    def getMembersByType(self, membType):
        ''' return a list of all members belonging to the same entity type '''
        memberList = []
        for member in self.members:
            if member.type == membType:
                memberList.append(member)
        return memberList
    
    
    @classmethod
    def getGroupByName(cls, groupName):
        ''' at import stage allows to relink an existing group or create a new one '''
        # existing group
        try:
            group = cls.__groupInstances[groupName]
        # new group with old imported name
        except KeyError:
            group = cls(groupName)
        return group
    
