# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

# /// tarmac
# description: Template for a Tarmac script
# inputs:
#     input_name:
#         type: str
#         description: Description of the input
#         default: "default_value"
#         required: true
#         example: "example"
# outputs:
#     output_name:
#         type: str
#         description: Description of the output
#         example: "example_output"
# ///

from tarmac.operations import Failure, OperationInterface, run


def Template(op: OperationInterface):
    raise Failure("This is a template script.")


run(Template)
