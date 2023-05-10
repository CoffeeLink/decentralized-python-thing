import json


"""Contains most stuff related to sending stuff from Node to Node"""

class MsgField:
    """ A message field is a name-value pair. The name is a string, and the value can be a string, int, or list.
    
    Attributes:
        name  [str]: The name of the field.
        value [str|int|list]: The value of the field.
    
    """

    name : str = None
    value : str = None
    
    def __init__(self, name : str, value : str | int | list) -> None:
        self.name = name
        self.value = value
    
    def addToDict(self, dictIn : dict) -> dict:
        """ Adds the field to a dictionary.

        Args:
            dictIn (dict): The dictionary to add the field to.

        Returns:
            dict: The dictionary with the field added.
        """
        dictIn[self.name] = self.value
        return dictIn

class Body:
    """ A message body is a collection of fields.

    Attributes:
        msg_type [str]: The type of the message. \n
        msg_id [int]: This is a unique identifier for the message. (Not required) \n
        msg_reply_to [int]: The ID of the message that this message is replying to. (Not required) \n
    """
    msg_type_ : MsgField = None
    msg_id_ : MsgField = None
    msg_reply_to_ : MsgField = None
    
    fields : list[MsgField] = None
    
    @property
    def msg_type(self) -> str:
        return self.msg_type_.value
    
    @msg_type.setter
    def msg_type(self, value : str) -> None:
        self.msg_type_ = MsgField("msg_type", value)
    
    @property
    def msg_id(self) -> int:
        return self.msg_id_.value
    
    @msg_id.setter
    def msg_id(self, value : int) -> None:
        self.msg_id_ = MsgField("msg_id", value)
    
    @property
    def msg_reply_to(self) -> int:
        return self.msg_reply_to_.value
    
    @msg_reply_to.setter
    def msg_reply_to(self, value : int) -> None:
        self.msg_reply_to_ = MsgField("msg_reply_to", value)
        
    def __init__(self, msg_type : str, msg_id : int = None, msg_reply_to : int = None) -> None:
        self.msg_type_ = MsgField("msg_type", msg_type)
        self.msg_id_ = MsgField("msg_id", msg_id)
        self.msg_reply_to_ = MsgField("msg_reply_to", msg_reply_to)
        self.fields = []
        
    def addField(self, name : str, value : str | int | list) -> None:
        """ Adds a field to the body.

        Args:
            name (str): The name of the field.
            value (str | int | list): The value of the field.
        """
        self.fields.append(MsgField(name, value))
        
    def setField(self, name : str, value : str | int | list) -> None:
        """ Sets the value of a field.
        If the field does not exist, it will be created.

        Args:
            name (str): The name of the field.
            value (str | int | list): The value of the field.
        """
        for field in self.fields:
            if field.name == name:
                field.value = value
                return
        
        self.addField(name, value)
    
    def delField(self, name : str) -> None:
        """ Deletes a field. If the field does not exist, nothing happens.

        Args:
            name (str): The name of the field.
        """
        for field in self.fields:
            if field.name == name:
                self.fields.remove(field)
                return
    
    def getField(self, name : str) -> str | int | list | None:
        """Returns The value of the field named : name, if it does not exist it will return None

        Args:
            name (str): the name of the field
        """
        for f in self.fields:
            if f.name == name:
                return f.value
        return None
            
    def toDict(self) -> dict:
        """ Converts the body to a dictionary. This is used to convert the body to JSON.

        Returns:
            dict: The dictionary representation of the body.
        """
        
        dictOut = {}
        if self.msg_type != None:
            dictOut = self.msg_type_.addToDict(dictOut)
        
        if self.msg_id != None:
            dictOut = self.msg_id_.addToDict(dictOut)
        
        if self.msg_reply_to != None:
            dictOut = self.msg_reply_to_.addToDict(dictOut)
        
        for field in self.fields:
            dictOut = field.addToDict(dictOut)
        
        return dictOut
    
    @classmethod
    def fromDict(self, dictIn : dict):
        """ Creates a body from a dictionary.

        Args:
            dictIn (dict): The dictionary to create the body from.

        Returns:
            Body: The body created from the dictionary.
        """
        body = Body(dictIn["msg_type"])
        if "msg_id" in dictIn:
            body.msg_id_.value = dictIn["msg_id"]
        
        if "msg_reply_to" in dictIn:
            body.msg_reply_to_.value = dictIn["msg_reply_to"]
        
        for key in dictIn:
            if key not in ["msg_type", "msg_id", "msg_reply_to"]:
                body.addField(key, dictIn[key])
        
        return body

    
class EchoBody(Body):
    """ A message body for an echo message.
    
    Attributes:
        echo [str]: The message to echo. \n
        msg_id [int]: This is a unique identifier for the message. (Not required) \n
        msg_reply_to [int]: The ID of the message that this message is replying to. (Not required) \n
    
    """
    
    echo_ : MsgField = None
    
    def __init__(self, echo : str, msg_id : int = None, msg_reply_to : int = None) -> None:
        super().__init__("echo", msg_id, msg_reply_to)
        self.echo_ = MsgField("echo", echo)
    
    def toDict(self) -> dict:
        
        """ Converts the body to a dictionary. This is used to convert the body to JSON.

        Returns:
            dict: The dictionary representation of the body.
        """
        
        dictOut = super().toDict()
        dictOut = self.echo_.addToDict(dictOut)
        
        return dictOut
    
    @property
    def echo(self) -> str:
        return self.echo_.value
    
    @echo.setter
    def echo(self, value : str) -> None:
        self.echo_ = MsgField("echo", value)

class EchoReplyBody(EchoBody):
    """ A message body for an echo reply message. This is a subclass of EchoBody.

    Args:
        echo [str]: The message to echo.\n
        msg_id [int]: This is a unique identifier for the message.\n
        msg_reply_to [int]: The ID of the message that this message is replying to.\n
    """
    
    def __init__(self, msg_id : int, msg_reply_to : int, echo : str) -> None:
        super().__init__(msg_id, msg_reply_to, echo)
        self.msg_type = "echo_ok"
    
    
class Payload:
    """ A message payload. This is the top level object that is sent over the network.

    Args:
        src [str]: The source of the message. This is the name of the sender.\n
        dest [str]: The destination of the message. This is the name of the receiver.\n
        body [Body]: The body of the message.\n
    """
    
    src : str = None
    dest : str = None
    body : Body = None
    
    def __init__(self, src : str, dest : str, body : Body) -> None:
        self.src = src
        self.dest = dest
        self.body = body
    
    def ToJson(self) -> str:
        """ Converts the payload to JSON. This is used to send the payload over the network.

        Returns:
            str: The JSON representation of the payload.
        """
        
        dictOut = {"src": self.src, "dest": self.dest, "body": self.body.toDict()}
        return json.dumps(dictOut)
    
    @staticmethod
    def FromJson(jsonIn : str):
        """ Converts a JSON string to a payload object.

        Args:
            jsonIn (str): The JSON string to convert.

        Returns:
            Payload: The payload object.
        """
        
        dictIn = json.loads(jsonIn)
        return Payload(dictIn["src"], dictIn["dest"], Body.fromDict(dictIn["body"]))
    
    def __str__(self) -> str:
        return self.ToJson()
