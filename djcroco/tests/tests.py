from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.utils import unittest
from django.test.client import Client

from .models import Example


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
    example = Example.objects.create(name='Test item',
        document=SimpleUploadedFile(TEST_DOC_NAME, TEST_DOC_DATA))

    # Get data out of the model
    instance = Example.objects.get(id=example.id)
    return instance


class CrocoTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.instance = initial_setup()

    def assertContains(self, test_value, expected_set):
        # That assert method does not exist in Py2.6
        msg = "%s does not contain %s" % (test_value, expected_set)
        self.assert_(test_value not in expected_set, msg)

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

    def test_document_thumbnail(self):
        # Ensure in-line image was returned
        self.assertContains(self.instance.document.thumbnail, 'data:image/png')

    def test_document_url(self):
        # Ensure correct URL was returned for `url`
        url = self.instance.document.url
        expected_url = reverse('croco_document_view',
            kwargs={'uuid': self.instance.document.uuid})
        self.assertEqual(url, expected_url)

        # Ensure correct redirect was made
        response = client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertContains(response._headers['location'][1], 'crocodoc.com')

    def test_document_content_url(self):
        # Ensure correct URL for `content_url`
        content_url = self.instance.document.content_url
        expected_url = reverse('croco_document_content',
            kwargs={'uuid': self.instance.document.uuid})
        self.assertEqual(content_url, expected_url)

        # Ensure correct response
        response = client.get(content_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response.content, 'crocodoc.com')

    def test_document_edit_url(self):
        # Ensure correct URL for `edit_url`
        edit_url = self.instance.document.edit_url(user_id=1, user_name='matt')
        kwargs = {
            'uuid': self.instance.document.uuid,
            'user_id': 1,
            'user_name': 'matt',
        }
        expected_url = reverse('croco_document_edit', kwargs=kwargs)
        self.assertEqual(edit_url, expected_url)

        # Ensure correct response
        response = client.get(edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response.content, 'crocodoc.com')

    def test_document_annotations(self):
        # Ensure correct URL for annotations
        annotations_url = self.instance.document.annotations_url(user_id=1)
        kwargs = {
            'uuid': self.instance.document.uuid,
            'user_id': 1,
        }
        expected_url = reverse('croco_document_annotations', kwargs=kwargs)
        self.assertEqual(annotations_url, expected_url)

        # Ensure correct response
        response = client.get(annotations_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response.content, 'crocodoc.com')

    def test_document_download(self):
        # Ensure correct URL for `download_document`
        document_url = self.instance.document.download_document
        expected_url = reverse('croco_document_download',
            kwargs={'uuid': self.instance.document.uuid})
        self.assertEqual(document_url, expected_url)

        # Ensure correct response
        # response = client.get(document_url)
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(len(response.content), 679)
        # self.assertEqual(response._headers['content-type'][1],
        #     'application/pdf')

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
