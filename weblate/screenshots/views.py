# -*- coding: utf-8 -*-
#
# Copyright © 2012 - 2017 Michal Čihař <michal@cihar.com>
#
# This file is part of Weblate <https://weblate.org/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404, redirect

from weblate.screenshots.models import Screenshot
from weblate.trans.views.helper import get_subproject
from weblate.trans.permissions import can_delete_screenshot
from weblate.utils import messages


class ScreenshotList(ListView):
    paginate_by = 25
    model = Screenshot

    def get_queryset(self):
        self.kwargs['component'] = get_subproject(
            self.request,
            self.kwargs['project'],
            self.kwargs['subproject']
        )
        return Screenshot.objects.filter(component=self.kwargs['component'])

    def get_context_data(self):
        result = super(ScreenshotList, self).get_context_data()
        result['object'] = self.kwargs['component']
        return result


class ScreenshotDetail(DetailView):
    model = Screenshot

    def get_object(self):
        obj = super(ScreenshotDetail, self).get_object()
        obj.component.check_acl(self.request)
        return obj


@require_POST
@login_required
def delete_screenshot(request, pk):
    obj = get_object_or_404(Screenshot, pk=pk)
    obj.component.check_acl(request)
    if not can_delete_screenshot(request.user, obj.component.project):
        raise PermissionDenied()

    kwargs = {
        'project': obj.component.project.slug,
        'subproject': obj.component.slug,
    }

    obj.delete()

    messages.info(request, _('Screenshot %s has been deleted.') % obj.name)

    return redirect('screenshots', **kwargs)
