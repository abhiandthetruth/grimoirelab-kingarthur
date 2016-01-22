# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#     Santiago Dueñas <sduenas@bitergia.com>
#     Alvaro del Castillo San Felix <acs@bitergia.com>
#

import inspect
import logging

import perceval.backends

from .errors import NotFoundError


logger = logging.getLogger(__name__)


def execute_perceval_backend(origin, backend, args):
    """Execute a backend of Perceval.

    Run a backend of Perceval for the given repository object.
    The type of the backend and its parameters are obtained
    from the given object.

    It will raise a `NotFoundError` in two cases: when the
    backend needed is not available or when any of the required
    parameters to run the backend are not found.
    """
    if backend not in perceval.backends.PERCEVAL_BACKENDS:
        raise NotFoundError(element=backend)

    klass = perceval.backends.PERCEVAL_BACKENDS[backend]
    kinit = find_signature_parameters(args, klass.__init__)
    kfetch = find_signature_parameters(args, klass.fetch)

    logging.debug("Running job %s (%s)", origin, backend)

    obj = klass(**kinit)
    for item in obj.fetch(**kfetch):
        yield item

    logging.debug("Job completed %s (%s)", origin, backend)


def find_signature_parameters(params, callable):
    """Find on a dict the parameters of a callable.

    Returns a dict with the parameters found on a callable. When
    any of the required parameters of a callable is not found,
    it raises a `NotFoundError` exception.
    """
    to_match = inspect_signature_parameters(callable)

    result = {}

    for p in to_match:
        name = p.name
        if name in params:
            result[name] =  params[name]
        elif p.default == inspect.Parameter.empty:
            # Parameters which its default value is empty are
            # considered as required
            raise NotFoundError(element=name)
    return result


def inspect_signature_parameters(callable):
    """Get the parameter of a callable.

    Parameters 'self' and 'cls' are filtered from the result.
    """
    signature = inspect.signature(callable)
    params = [v for p, v in signature.parameters.items() \
              if p not in ('self', 'cls')]
    return params
