from abc import ABC

from flask_restful import reqparse


class Specification:

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def filtering_value_is_satisfied(self, candidate, args):
        raise NotImplementedError()


class And(Specification):
    def __init__(self, *specifications):
        self.specifications = specifications

    def __and__(self, other):
        if isinstance(other, And):
            self.specifications += other.specifications
        else:
            self.specifications += (other, )
        return self

    def filtering_value_is_satisfied(self, candidate, args):
        satisfied = all([
            specification.filtering_value_is_satisfied(candidate, args)
            for specification in self.specifications
        ])
        return satisfied


class Or(Specification):
    def __init__(self, *specifications):
        self.specifications = specifications

    def __or__(self, other):
        if isinstance(other, Or):
            self.specifications += other.specifications
        else:
            self.specifications += (other,)
        return self

    def filtering_value_is_satisfied(self, candidate, args):
        satisfied = any([
            specification.filtering_value_is_satisfied(candidate, args)
            for specification in self.specifications
        ])
        return satisfied


class MinimalPageNumber(Specification):
    def filtering_value_is_satisfied(self, model, args):
        if args['pageNumberMin']:
            return model['pageNumber'] > int(args['pageNumberMin'])
        else:
            return True


class MaximalPageNumber(Specification):
    def filtering_value_is_satisfied(self, model, args):
        if args['pageNumberMax']:
            return model['pageNumber'] < int(args['pageNumberMax'])
        else:
            return True


class Payment(Specification):
    def filtering_value_is_satisfied(self, model, args):
        if args['payment']:
            return model['payment'] == args['payment']
        else:
            return True


class MinimalPrice(Specification):
    def filtering_value_is_satisfied(self, model, args):
        if args['minPrice']:
            return model['price'] > int(args['minPrice'])
        else:
            return True


class MaximalPrice(Specification):
    def filtering_value_is_satisfied(self, model, args):
        if args['maxPrice']:
            return model['price'] < int(args['maxPrice'])
        else:
            return True
