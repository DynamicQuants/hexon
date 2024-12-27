import type { EntityType } from '../entity';
import { type GetEntityProps } from '../generics';
import type { FieldValue, Filter, LogicalOperator, Operators } from './filter';

/**
 * Criteria class for filtering entities. It can contain multiple filters or conditions with logical
 * operators.
 */
export class Criteria<E extends EntityType, P = GetEntityProps<E>> {
  private logicalOperator: LogicalOperator;
  private filters: (Filter<P> | Criteria<E, P>)[];

  constructor(logicalOperator: LogicalOperator = 'AND') {
    this.logicalOperator = logicalOperator;
    this.filters = [];
  }

  public addFilter<K extends keyof P>(
    field: K,
    operator: Operators<P[K]>,
    value: FieldValue<P, K>,
  ): Criteria<E, P> {
    this.filters.push({ field, operator, value });
    return this;
  }

  public addCriteria(criteria: Criteria<E, P>): Criteria<E, P> {
    this.filters.push(criteria);
    return this;
  }

  public getFilters(): (Filter<P> | Criteria<E, P>)[] {
    return this.filters;
  }

  public getLogicalOperator(): LogicalOperator {
    return this.logicalOperator;
  }
}
