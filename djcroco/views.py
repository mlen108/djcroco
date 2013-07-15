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
            params = {}
            qs_params = request.GET

            bool_params = ("editable", "admin", "downloadable", "copyprotected", "demo")
            for p in bool_params:
                if p in qs_params:
                    params[p] = True

            if 'user_id' in qs_params and 'user_name' in qs_params:
                params['user'] = {
                    'id': qs_params['user_id'],
                    'name': qs_params['user_name'],
                }

            if 'filter' in qs_params:
                params['filter'] = qs_params['filter']

            if 'sidebar' in qs_params:
                params['sidebar'] = qs_params['sidebar']

            session = crocodoc.session.create(uuid, **params)
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
            qs_params = request.GET
            pdf = True
            annotated = filter_by = None
            if 'annotated' in qs_params and qs_params['annotated'].lower() == 'true':
                annotated = True
            if 'filter' in qs_params:
                filter_by = True
            file = crocodoc.download.document(uuid, pdf=pdf, annotated=annotated,
                user_filter=filter_by)
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
            width = height = 100
            if 'size' in request.GET:
                width, height = request.GET['size'].split('x')
            image = crocodoc.download.thumbnail(uuid, width=int(width),
                height=int(height))
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
