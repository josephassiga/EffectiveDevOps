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

from troposphere.iam import (
    InstanceProfile,
    PolicyType as IAMPolicy,
    Role);

from awacs.aws import (
    Action,
    Allow,
    Policy,
    Principal,
   Statement);

from awacs.sts import AssumeRole;


ApplicationName = "jenkins";

ApplicationPort = "8080";

GithubAccount = "josephassiga";

GithubAsibleURL = "https://github.com/{}/Ansible".format(GithubAccount);

AnsiblePullCmd = "/usr/local/ansible-pull -U {}.yml -i localhost".format(GithubAsibleURL,ApplicationName);
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
    "pip install ansible",
    AnsiblePullCmd,
    "echo '*/10 * * * * {}' > /etc/cron.d/ansible-pull".format(AnsiblePullCmd)
]))

template.add_resource(Role(
    "Role",
    AssumeRolePolicyDocument=Policy(
      Statement=[
          Statement(
              Effect=Allow,
              Action=[AssumeRole],
              Principal=Principal("Service",["ec2.awsamazon.com"])
          )
      ]
    )
));

template.add_resource(InstanceProfile(
    "InstanceProfile",
    Path="/",
    Roles=[Ref("Role")]
));

template.add_resource(ec2.Instance(
    "instance",
    ImageId="ami-d834aba1",
    InstanceType="t2.micro",
    SecurityGroups=[Ref("SecurityGroup")],
    KeyName=Ref("KeyPair"),
    UserData=ud,
    IamInstanceProfile=Ref("InstanceProfile")
));


template.add_output(Output(
    "InstancePulicIp",
    Description="Public Ip of our Instance",
    Value=GetAtt("instance", "PublicIp")
));

template.add_output(Output(
    "WebUrl",
    Description="Application Endpoint",
    Value=Join("", ["http:/", GetAtt("instance", "PublicDnsName"), ":", ApplicationPort])
));

print(template.to_json());
