import codecs
from flask_swagger_codegen import writer, parser, model
from flask_swagger_codegen.resolver import FlaskModelResolver

with codecs.open('docs/API.yml', 'r', 'utf-8') as f:
    swagger = parser.SwaggerParser().parse_yaml(f)

m = FlaskModelResolver(swagger).resolve()

writer.write(m, 'student-api', 'student_api')

