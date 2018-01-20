from ipaddress import ip_network;

from ipify import get_ip;

from troposphere import (
    Base64,
    ec2,
    GetAtt,
    Join,
    Output,
    Parameter,
    Ref,
    Template);




ApplicationPort = "3000";

PublicCidrPort = str(ip_network(get_ip()));

template = Template();

template.add_description("Effective DEVOPS in AWS : Hello World Web Application");

template.add_parameter(Parameter(
    "KeyPair",
    Description="Name of an existing EC2 KeyPair to SSH",
    Type="AWS::EC2::KeyPair::KeyName",
    ConstraintDescription="Must be the name of an existing EC2 KeyPair."
));

template.add_resource(
  ec2.SecurityGroup(
      "SecurityGroup",
      GroupDescription="Allow SSH and TCP/{}".format(ApplicationPort),
      SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="22",
            ToPort="22",
            CidrIp=PublicCidrPort
        ),
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort=ApplicationPort,
            ToPort=ApplicationPort,
            CidrIp="0.0.0.0/0"
        )
      ]
  )
);

ud = Base64(Join('\n', [
    "#!/bin/bash",
    "sudo yum install --enablerepo=epel -y nodejs",
    "wget http://bit.ly/2vESNuc -O /home/ec2-user/helloworld.js",
    "wget http://bit.ly/2vVvT18 -O /etc/init/helloworld.conf",
    "start helloworld"
]))

template.add_resource(ec2.Instance(
    "instance",
    ImageId="ami-d834aba1",
    InstanceType="t2.micro",
    SecurityGroups=[Ref("SecurityGroup")],
    KeyName=Ref("KeyPair"),
    UserData=ud
));


template.add_output(Output(
    "InstancePulicIp",
    Description="Public Ip of our Instance",
    Value=GetAtt("instance","PublicIp")
));

template.add_output(Output(
    "WebUrl",
    Description="Application Endpoint",
    Value=Join("",["http:/",GetAtt("instance","PublicDnsName"),":",ApplicationPort])
));


print(template.to_json());
