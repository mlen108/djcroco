import mimetypes

import crocodoc
from django.db.models.loading import get_model
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, Http404
from django.views.generic.detail import BaseDetailView, DetailView

from .models import CROCO_MODEL

# TODO: check other types of instances
if isinstance(CROCO_MODEL, str):
    app_label, model_name = CROCO_MODEL.split('.', 1)
    _croco_model = get_model(app_label, model_name)
    if _croco_model is None:
        msg = "Could not find '{0}' model in app '{1}'."
        raise ImproperlyConfigured(msg.format(model_name, app_label))


class CrocoDownload(DetailView):
    model = _croco_model

    def render_to_response(self, context, **response_kwargs):
        obj = context.pop('object')
        if not obj.file:
            raise Http404('File does not exist.')

        if not obj.is_downloadable:
            raise Http404('File is not downloadable.')

        # get the name of file without path
        filename = obj.file.name.split('/')[-1]
        mimetype, _ = mimetypes.guess_type(filename)

        response = HttpResponse(mimetype=mimetype)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        response.write(obj.file.read())
        return response


class CrocoView(BaseDetailView):
    model = _croco_model

    def get(self, request, *args, **kwargs):
        obj = self.get_object()

        try:
            session = crocodoc.session.create(obj.crocodoc_uuid)
        except crocodoc.CrocodocError as e:
            return HttpResponse(status=e.status_code)

        # TODO:
        croco_url = 'https://crocodoc.com/view/{0}'

        resp = {
            'content': croco_url.format(session),
        }

        return HttpResponse(**resp)
