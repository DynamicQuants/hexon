import { Either } from 'effect';

import { Criteria } from '@/aggregates';

import { type User, UserName, UserRole, UserRoleEnum } from './common';

describe('Criteria', () => {
  it('Should create a criteria with a filter', () => {
    const criteriaResult = Either.Do.pipe(
      Either.bind('roles', () =>
        Either.all([UserRoleEnum.ADMIN, UserRoleEnum.SALES].map((role) => UserRole.create(role))),
      ),
      Either.bind('name', () => UserName.create('John Doe')),
      Either.map(({ roles, name }) =>
        new Criteria<User>()
          .addFilter('roles', 'contains', roles)
          .addFilter('name', 'equals', name),
      ),
    );

    expect(Either.isRight(criteriaResult)).toBeTruthy();

    if (Either.isRight(criteriaResult)) {
      const criteria = criteriaResult.right;

      expect(criteria).toBeInstanceOf(Criteria);

      console.log(criteria);

      // const filter = criteria.getFilters();
      // expect(name).toBeDefined();
    }
  });
});
