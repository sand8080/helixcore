from helixcore.db.sql import And, Any, NullLeaf, Select, Columns
from helixcore.db.wrapper import SelectedMoreThanOneRow, ObjectNotFound, fetchone_dict
import helixcore.mapping.actions as mapping


class ObjectsFilter(object):
    cond_map = []

    def __init__(self, filter_params, paging_params, ordering_params, obj_class):
        self.filter_params = filter_params
        self.paging_params = paging_params
        self.ordering_params = ordering_params if ordering_params else 'id'
        self.obj_class = obj_class

    def _cond_by_filter_params(self):
        cond = NullLeaf()
        for p_name, db_f_name, c in self.cond_map:
            if p_name in self.filter_params:
                if c == Any:
                    cond = And(cond, c(self.filter_params[p_name], db_f_name))
                else:
                    cond = And(cond, c(db_f_name, self.filter_params[p_name]))
        return cond

    def _get_paging_params(self):
        return self.paging_params.get('limit'), self.paging_params.get('offset', 0)

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
