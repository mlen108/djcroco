import crocodoc

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.generic import View


class CrocoDocumentView(View):
    redirect = None

    def get(self, request, *args, **kwargs):
        uuid = kwargs.pop('uuid', None)
        if uuid is None:
            raise Http404

        try:
            session = crocodoc.session.create(uuid)
        except crocodoc.CrocodocError as e:
            return HttpResponse(content=e.response_content,
                status=e.status_code)

        url = 'https://crocodoc.com/view/{0}'.format(session)

        if self.redirect:
            return HttpResponseRedirect(url)
        return HttpResponse(content=url)


class CrocoDocumentDownload(View):
    """
    Downloads document from Crocodoc in PDF format.
    TODO: allow to download original version
    """
    def get(self, request, *args, **kwargs):
        uuid = kwargs.pop('uuid', None)
        if uuid is None:
            raise Http404

        try:
            file = crocodoc.download.document(uuid, True)
        except crocodoc.CrocodocError as e:
            return HttpResponse(content=e.response_content,
                status=e.status_code)

        response = HttpResponse(mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=%s.pdf' % uuid
        response.write(file)
        return response


class CrocoDocumentEdit(View):
    def get(self, request, *args, **kwargs):
        uuid = kwargs.pop('uuid', None)
        user_id = kwargs.pop('user_id', None)
        user_name = kwargs.pop('user_name', None)
        if not (uuid and user_id and user_name):
            raise Http404

        try:
            kwargs = {
                'editable': True,
                'user': {
                    'id': user_id,
                    'name': user_name,
                }
            }
            session = crocodoc.session.create(uuid, **kwargs)
        except crocodoc.CrocodocError as e:
            return HttpResponse(content=e.response_content,
                status=e.status_code)

        url = 'https://crocodoc.com/view/{0}'.format(session)

        return HttpResponse(content=url)


class CrocoDocumentAnnotations(View):
    def get(self, request, *args, **kwargs):
        uuid = kwargs.pop('uuid', None)
        user_id = kwargs.pop('user_id', None)
        if not (uuid and user_id):
            raise Http404

        try:
            session = crocodoc.session.create(uuid, filter=user_id)
        except crocodoc.CrocodocError as e:
            return HttpResponse(content=e.response_content,
                status=e.status_code)

        url = 'https://crocodoc.com/view/{0}'.format(session)

        return HttpResponse(content=url)


class CrocoThumbnailDownload(View):
    def get(self, request, *args, **kwargs):
        uuid = kwargs.pop('uuid', None)
        if uuid is None:
            raise Http404

        try:
            image = crocodoc.download.thumbnail(uuid)
        except crocodoc.CrocodocError as e:
            return HttpResponse(content=e.response_content,
                status=e.status_code)

        response = HttpResponse(mimetype='image/png')
        response['Content-Disposition'] = 'attachment; filename=%s.png' % uuid
        response.write(image)
        return response


class CrocoTextDownload(View):
    def get(self, request, *args, **kwargs):
        uuid = kwargs.pop('uuid', None)
        if uuid is None:
            raise Http404

        try:
            text = crocodoc.download.text(uuid)
        except crocodoc.CrocodocError as e:
            return HttpResponse(content=e.response_content,
                status=e.status_code)

        return HttpResponse(content=text)
