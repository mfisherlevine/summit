PS1="\[\e[36m\]\u \[\e[33m\]:\[\e[32m\]\w$\[\e[37m\] "

# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi

# User specific environment and startup programs

export PYTHONDONTWRITEBYTECODE=True
export DISPLAY=

ignoreeof=3

alias eupss="eups list -s | cut -f-1"
alias eups_local="eups list -s | cut -f-1 | grep LOCAL"
alias eups_local="packageStatus"
alias count="ls -1 | wc -l"
alias count_all="find -maxdepth 1 -type d | while read -r dir; do printf "%s:\t" "$dir"; find "$dir" -type f | wc -l; done"
alias gs="git status"
alias gc="git checkout"
alias gcm="git checkout master"
alias gd="git diff"
alias gl="git log"
alias dirsize="du -hs * | sort -hr"
alias ls='ls --color=auto'
alias ldir='ls -ld */'
alias git-squash-to-base="git reset \$(git merge-base master \$(git rev-parse --abbrev-ref HEAD))"


# cd up to n dirs
# using:  cd.. 10   cd.. dir
function cd_up() {
  case $1 in
    *[!0-9]*)                                          # if no a number
      cd $( pwd | sed -r "s|(.*/$1[^/]*/).*|\1|" )     # search dir_name in current path, if found - cd to it
      ;;                                               # if not found - not cd
    *)
      cd $(printf "%0.0s../" $(seq 1 $1));             # cd ../../../../  (N dirs)
    ;;
  esac
}
alias 'cd..'='cd_up' 

function ggrep(){
  grep -r --include="*.py" --exclude-dir="build/" -n --color "$1" . $2
}

function dgrep(){
  grep -r --include="*.py" --exclude-dir="build/" -n --color "def $1" . $2
}

function cgrep(){
  grep -r --include="*.py"  --exclude-dir="build/" -n --color "class $1" . $2
}

function ygrep(){
  grep -r --include="*.yaml"  --exclude-dir="build/" -n --color "$1" . $2
}

function ipygrep(){
  grep -r --include="*.ipynb"  --exclude-dir="build/" -n --color "$1" . $2
}

