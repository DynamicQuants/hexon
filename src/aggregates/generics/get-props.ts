import type { EntityProperty, EntityType } from '../entity';

/**
 * Extract the entity props that are value objects.
 */
export type GetEntityProps<T extends EntityType> = {
  [K in keyof T as T[K] extends EntityProperty | EntityProperty[] ? K : never]: T[K] extends
    | EntityProperty
    | EntityProperty[]
    ? T[K]
    : never;
};
