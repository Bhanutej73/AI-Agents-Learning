from mcp.server.fastmcp import FastMCP

mcp=FastMCP("Math")

@mcp.tool()
def add(a:int, b:int)->int:
    """
    Adds two integers.

    Args:
        a (int): The first integer.
        b (int): The second integer.

    Returns:
        int: Adds two numbers
    """
    return a + b

@mcp.tool()
def multiply(a:int, b:int)->int:
    """
    Multiplies two integers.

    Args:
        a (int): The first integer.
        b (int): The second integer.

    Returns:
        int: Multiplies two numbers
    """
    return a * b

if __name__=="__main__":
    mcp.run(transport="stdio") #We can run it in command line, and get the response in the command line. We can also run it in a web server, and get the response in a web page.

#The transport="stdio" argument talls the seever to:
#Use the standard input/output (stdio) for communication. This means that the server will read requests from the standard input (stdin) and write responses to the standard output (stdout). This is useful for running the server in a command-line environment, where you can interact with it directly through the terminal.