import time

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.utils import unittest
from django.template import Context, Template
from django.test.client import Client

from .models import Example, NullableExample


# simple 1-page pdf saying 'Hello, world!'
TEST_DOC_DATA = (  # Multiline string, not tuple.
    '%PDF-1.7\n\n1 0 obj  % entry point\n<<\n  /Type /Catalog\n  /Pages 2 0 '
    'R\n>>\nendobj\n\n2 0 obj\n<<\n  /Type /Pages\n  /MediaBox [ 0 0 200 200 '
    ']\n  /Count 1\n  /Kids [ 3 0 R ]\n>>\nendobj\n\n3 0 obj\n<<\n  /Type '
    '/Page\n  /Parent 2 0 R\n  /Resources <<\n    /Font <<\n      /F1 4 0 R \n'
    '    >>\n  >>\n  /Contents 5 0 R\n>>\nendobj\n\n4 0 obj\n<<\n  /Type '
    '/Font\n  /Subtype /Type1\n  /BaseFont /Times-Roman\n>>\nendobj\n\n5 0 obj'
    '  % page content\n<<\n  /Length 44\n>>\nstream\nBT\n70 50 TD\n/F1 12 '
    'Tf\n(Hello, world!) Tj\nET\nendstream\nendobj\n\nxref\n0 6\n0000000000 '
    '65535 f \n0000000010 00000 n \n0000000079 00000 n \n0000000173 00000 n '
    '\n0000000301 00000 n \n0000000380 00000 n \ntrailer\n<<\n  /Size 6\n  '
    '/Root 1 0 R\n>>\nstartxref\n492\n%%EOF\n'
)
TEST_DOC_NAME = 'test_doc_file.pdf'


client = Client()


def initial_setup():
    """ Inits all here as we do not want doing it in *every* test """
    # Create sample data
    example = Example.objects.create(
        name='Test item',
        document=SimpleUploadedFile(TEST_DOC_NAME, TEST_DOC_DATA))

    # Get data out of the model
    instance = Example.objects.get(id=example.id)
    return instance


class CrocoTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.instance = initial_setup()

    def setUp(self):
        # there is a race conditions somewhere so sleep between each test
        time.sleep(1)

    def render(self, tmpl):
        tmplout = "{% load croco_tags %}{% autoescape off %}"
        tmplout += tmpl
        tmplout += "{% endautoescape %}"
        return Template(tmplout).render(Context({'obj': self.instance}))

    def assertContains(self, test_value, expected_set):
        # That assert method does not exist in Py2.6
        msg = "%s does not contain %s" % (test_value, expected_set)
        self.assert_(test_value not in expected_set, msg)

    def test_document_empty(self):
        # Ensure document can be empty
        instance = Example.objects.create(name='Test empty')
        self.assertEqual(instance.document, '')

    def test_document_null(self):
        # Ensure document can be null
        instance = NullableExample.objects.create(name='Test empty')
        self.assertEqual(instance.document, None)

    def test_document_name(self):
        # Ensure document has correct name
        self.assertEqual(self.instance.document.name, TEST_DOC_NAME)

    def test_document_size(self):
        # Ensure correct size
        self.assertEqual(self.instance.document.size, 679)
        self.assertEqual(self.instance.document.size_human, '679 bytes')

    def test_document_type(self):
        # Ensure correct file type
        self.assertEqual(self.instance.document.type, 'pdf')

    def test_document_uuid(self):
        # Ensure correct length of UUID
        # UUID is 32 long chars, but there is 36 including dash chars
        uuid = self.instance.document.uuid
        self.assertEqual(len(uuid), 36)

    def test_document_url(self):
        # Ensure correct URL was returned for `url`
        url = self.instance.document.url
        expected_url = reverse('croco_document_url',
            kwargs={'uuid': self.instance.document.uuid})
        self.assertEqual(url, expected_url)

        # Ensure correct redirect was made
        response = client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertContains(response._headers['location'][1], 'crocodoc.com')

    def test_document_url_with_annotations(self):
        tmpl = "{{ obj.document.url|annotated:'true' }}"
        response = client.get(self.render(tmpl))
        self.assertEqual(response.status_code, 302)
        self.assertContains(response._headers['location'][1], 'crocodoc.com')

    def test_document_url_with_editable_and_user(self):
        tmpl = "{{ obj.document.url|editable:'true'|user_id:'1'|user_name:'admin' }}"
        response = client.get(self.render(tmpl))
        self.assertEqual(response.status_code, 302)
        self.assertContains(response._headers['location'][1], 'crocodoc.com')

    def test_document_content_url(self):
        # Ensure correct URL for `content_url`
        content_url = self.instance.document.content_url
        expected_url = reverse('croco_document_content_url',
            kwargs={'uuid': self.instance.document.uuid})
        self.assertEqual(content_url, expected_url)

        # Ensure correct response
        response = client.get(content_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response.content, 'crocodoc.com')

    def test_document_content_url_with_user_filter(self):
        tmpl = "{{ obj.document.content_url|user_filter:'1,2' }}"
        response = client.get(self.render(tmpl))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response.content, 'crocodoc.com')

    def test_document_download(self):
        # Ensure correct URL for `download_document`
        document_url = self.instance.document.download_document
        expected_url = reverse('croco_document_download',
            kwargs={'uuid': self.instance.document.uuid})
        self.assertEqual(document_url, expected_url)

        # Ensure correct response
        response = client.get(document_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 679)
        self.assertEqual(response._headers['content-type'][1],
            'application/pdf')

    def test_document_download_with_annotations(self):
        tmpl = "{{ obj.document.download_document|annotated:'true' }}"
        response = client.get(self.render(tmpl))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 1049)
        self.assertEqual(response._headers['content-type'][1],
            'application/pdf')

    def test_document_thumbnail_custom_field(self):
        # get filename with correct path
        uuid = self.instance.document.uuid
        filename = self.instance.my_thumbnail.field.upload_to + uuid
        # thumbnail should not exist yet
        self.assertFalse(self.instance.my_thumbnail.storage.exists(filename))
        # create thumbnail
        self.instance.document.thumbnail
        # ensure it is saved in custom thumbnail field
        self.assertTrue(self.instance.my_thumbnail.storage.exists(filename))

    def test_thumbnail_download(self):
        # Ensure correct URL for `download_thumbnail`
        thumbnail_url = self.instance.document.download_thumbnail
        expected_url = reverse('croco_thumbnail_download',
            kwargs={'uuid': self.instance.document.uuid})
        self.assertEqual(thumbnail_url, expected_url)

        # Ensure correct response
        response = client.get(thumbnail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._headers['content-type'][1], 'image/png')

    def test_thumbnail_download_with_custom_size(self):
        tmpl = "{{ obj.document.download_thumbnail|size:'121x121' }}"
        response = client.get(self.render(tmpl))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._headers['content-type'][1], 'image/png')

    def test_text_download(self):
        # Ensure correct URL for `download_text`
        text_url = self.instance.document.download_text
        expected_url = reverse('croco_text_download',
            kwargs={'uuid': self.instance.document.uuid})
        self.assertEqual(text_url, expected_url)

        # Ensure text is not returned for test account (an account without
        # extracting text feature enabled)
        response = client.get(text_url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, '{"error": "text not available"}')
