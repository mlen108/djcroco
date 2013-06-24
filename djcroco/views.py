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
