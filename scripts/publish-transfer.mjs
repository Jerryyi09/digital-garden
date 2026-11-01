export function homeServerRsyncArgs(target) {
  return [
    "-rltp",
    "--chmod=Du=rwx,Dgo=rx,Fu=rw,Fgo=r",
    "-e", "ssh -F /dev/null -o BatchMode=yes -p 2222 -i /Users/jerryyi/.ssh/id_rsa",
    "public/",
    target,
  ]
}
