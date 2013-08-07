#!/usr/bin/env python
#
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in the LICENSE
# file at the top-level directory of this package.
#
#


class Relationship(object):

    '''ZenPack Relationship Management'''

    relationships = {}

    def __init__(self,
                 ZenPack,
                 componentA,
                 componentB,
                 type_='1-M',
                 contained=True,
                 *args,
                 **kwargs
                 ):
        """Args:
                ZenPack:  A ZenPack Class instance
                componentA: Parent component string id
                componentB: Child component string id
                type_: Relationship type_.  Valid inputs [1-1,1-M,M-M]
                contained: ComponentA contains ComponentB True or False
        """
        self.ZenPack = ZenPack
        from Component import Component
        lookup = Component.lookup
        self.components = lookup(
            ZenPack, componentA), lookup(ZenPack, componentB)
        self.id = '%s %s' % (self.components[0].id, self.components[1].id)
        self.type_ = type_
        self.contained = contained

        # Register the relationship on a zenpack so we can find it later.
        self.ZenPack.registerRelationship(self)

        Relationship.relationships[self.id] = self

    def hasComponent(self, component):
        '''Return True if this relationship has this component inside.'''
        for c in self.components:
            if component.id == c.id:
                return True
        return False

    def hasChild(self, component):
        '''Return True if this relationship has this component inside
           in the child position.'''
        if component.id == self.components[1].id:
            return True
        return False

    @classmethod
    def find(self, component, contained=None, first=None, types=None):
        '''return all the relationships that match the input request.

           Args:
              component: A parent or child component in this relationship
              contained: True/False containment relationship
              first: True/False  True if we are searching for the Parent
                                 Component in the relationship.

              types_: 1-1, 1-M, M-M are valid relationship types_.
                     1-1: One to One
                     1-M: One to Many
                     M-M: Many to Many
        '''

        rels = []
        for rel in Relationship.relationships.values():
            if rel.hasComponent(component):
                if not contained is None:
                    if not rel.contained == contained:
                        continue
                if not first is None:
                    if not rel.first(component) == first:
                        continue
                if not types is None:
                    if isinstance(types, basestring):
                        if rel.type_ == types:
                            continue
                    else:
                        if not rel.type_ in types:
                            continue

                rels.append(rel)
        return sorted(rels)

    def first(self, component):
        '''Is this the first component in the relationship'''
        if component.id == self.components[0].id:
            return True
        return False

    def child(self):
        '''Return the child component.'''
        return self.components[1]

    def toString(self, component):
        '''Write the relationship into a string format based on the component
           as a frame of reference. This is a 3.X and 4.X string format.'''

        if self.first(component):
            compA = self.components[1]
            compB = self.components[0]
        else:
            compA = self.components[0]
            compB = self.components[1]

        if self.contained:
            contained = 'Cont'
        else:
            contained = ''

        if self.type_ == '1-1':
            direction = 'ToOne(ToOne'
            return "('{0}', {1}, '{2}', '{3}',)),".format(compA.relname,
                                                          direction,
                                                          compA.id,
                                                          compB.relname)
        elif self.type_ == '1-M':
            if self.first(component):
                direction = 'ToMany{0}(ToOne'.format(contained)
                return "('{0}', {1}, '{2}', '{3}',)),".format(compA.relnames,
                                                              direction,
                                                              compA.id,
                                                              compB.relname)
            else:
                direction = 'ToOne(ToMany{0}'.format(contained)
                return "('{0}', {1}, '{2}', '{3}',)),".format(compA.relname,
                                                              direction,
                                                              compA.id,
                                                              compB.relnames)
        elif self.type_ == 'M-M':
            if self.first(component):
                direction = 'ToMany(ToMany{0}'.format(contained)

            else:
                direction = 'ToMany{0}(ToMany'.format(contained)

            return "('{0}', {1}, '{2}', '{3}',)),".format(compA.relnames,
                                                          direction,
                                                          compA.id,
                                                          compB.relnames)
