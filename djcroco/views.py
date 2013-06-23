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
            return HttpResponse(status=e.status_code)

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
            return HttpResponse(status=e.status_code)

        response = HttpResponse(mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=%s.pdf' % uuid
        response.write(file)
        return response
