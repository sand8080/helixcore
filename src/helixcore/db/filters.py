from helixcore.db.sql import (And, Any, NullLeaf, Select, Columns, AnyOf, Or,
    Scoped, Eq)
from helixcore.db.wrapper import SelectedMoreThanOneRow, ObjectNotFound, fetchone_dict
from helixcore import mapping
from helixcore.db.dataobject import Currency
from helixcore.error import CurrencyNotFound


def build_index(objs, idx_field='id'):
    return dict([(getattr(obj, idx_field), obj) for obj in objs])


def build_complex_index(objs, idx_fields, delimiter='_'):
    result = {}
    for obj in objs:
        keys_values = ['%s' % getattr(obj, idx_field) for idx_field in idx_fields]
        key = delimiter.join(keys_values)
        result[key] = obj
    return result


def build_dicts_index(dicts, idx_field='id'):
    return dict([(d[idx_field], d) for d in dicts])


class ObjectsFilter(object):
    '''[(p_name, db_f_name, operation_class), ...]
    '''
    cond_map = []

    def __init__(self, filter_params, paging_params, ordering_params, obj_class):
        self.filter_params = filter_params
        self.paging_params = paging_params
        self.ordering_params = ordering_params if ordering_params else 'id'
        self.obj_class = obj_class

    def _is_composed_parameter(self, p):
        return isinstance(p, (list, tuple))

    def _compose_cond(self, cond, p_value, db_f_name, c, composer):
        if c in (Any, AnyOf):
            return composer(cond, c(p_value, db_f_name))
        else:
            return composer(cond, c(db_f_name, p_value))

    def _cond_by_filter_params(self):
        cond = NullLeaf()
        for p_name, db_f_name, c in self.cond_map:
            if p_name in self.filter_params:
                if self._is_composed_parameter(p_name):
                    cond_el = NullLeaf()
                    p_value = self.filter_params[p_name]
                    for p_value_el, db_f_name_el, c_el in zip(p_value, db_f_name, c):
                        cond_el = self._compose_cond(cond_el, p_value_el,
                            db_f_name_el, c_el, Or)
                    cond = And(cond, Scoped(cond_el))
                else:
                    cond = self._compose_cond(cond, self.filter_params[p_name],
                        db_f_name, c, And)
        return cond

    def _get_paging_params(self):
        return self.paging_params.get('limit', None), self.paging_params.get('offset', 0)

    def filter_objs(self, curs, for_update=False):
        cond = self._cond_by_filter_params()
        limit, offset = self._get_paging_params()
        return mapping.get_list(curs, self.obj_class, cond=cond, order_by=self.ordering_params,
            limit=limit, offset=offset, for_update=for_update)

    def filter_objs_count(self, curs):
        cond = self._cond_by_filter_params()
        q = Select(self.obj_class.table, columns=[Columns.COUNT_ALL], cond=cond)
        curs.execute(*q.glue())
        count_dict = fetchone_dict(curs)
        _, count = count_dict.popitem()
        return int(count)

    def filter_one_obj(self, curs, for_update=False):
        objs = self.filter_objs(curs, for_update=for_update)
        if len(objs) > 1:
            raise SelectedMoreThanOneRow
        elif len(objs) == 0:
            raise ObjectNotFound
        else:
            return objs[0]

    def filter_counted(self, curs):
        return self.filter_objs(curs), self.filter_objs_count(curs)


class EnvironmentObjectsFilter(ObjectsFilter):
    def __init__(self, environment_id, filter_params, paging_params, ordering_params, obj_class):
        super(EnvironmentObjectsFilter, self).__init__(filter_params, paging_params, ordering_params, obj_class)
        self.environment_id = environment_id

    def _cond_by_filter_params(self):
        cond = super(EnvironmentObjectsFilter, self)._cond_by_filter_params()
        cond = And(cond, Eq('environment_id', self.environment_id))
        return cond


class InSessionFilter(ObjectsFilter):
    def __init__(self, session, filter_params, paging_params, ordering_params, obj_class):
        super(InSessionFilter, self).__init__(filter_params, paging_params, ordering_params, obj_class)
        self.session = session

    def _cond_by_filter_params(self):
        cond = super(InSessionFilter, self)._cond_by_filter_params()
        cond = And(cond, Eq('environment_id', self.session.environment_id))
        return cond


class CurrencyFilter(ObjectsFilter):
    cond_map = [
        ('id', 'id', Eq),
        ('code', 'code', Eq),
    ]

    def __init__(self, filter_params, paging_params, ordering_params):
        super(CurrencyFilter, self).__init__(filter_params, paging_params,
            ordering_params, Currency)

    def filter_one_obj(self, curs, for_update=False):
        try:
            return super(CurrencyFilter, self).filter_one_obj(curs,
                for_update=for_update)
        except (ObjectNotFound, SelectedMoreThanOneRow):
            raise CurrencyNotFound(**self.filter_params)


