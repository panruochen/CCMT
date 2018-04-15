
make_exclude_list_mydroid()
{
	local i exclude_components exclude_list

	exclude_components='clang/darwin-x86* misc/darwin-x86* gcc/darwin-x86*
		gcc/linux-x86/mips gcc/linux-x86/x86 gcc/linux-x86/aarch64
		tools/darwin-x86* python/darwin-x86* sdk/tools/darwin-x86*
		misc/android-mips* android-emulator/darwin-x86_64 sdk/tools/darwin
		'
	exclude_list='--exclude out/*'
	for i in $exclude_components
	do
		exclude_list="$exclude_list --exclude prebuilts/$i"
	done
	echo "$exclude_list"
}

make_exclude_list_kernel()
{
	:
}

pack_common() {
	local i tmpDir excludeList srcDir baseName mainName

	srcDir="$1"
	shift 1

	if [ -z "$srcDir" ]; then
		echo "srcDir is not set" >&2
		exit 1
	fi
	if [ ! -d "$srcDir" ]; then
		echo "$srcDir is not a directory" >&2
		exit 1
	fi
	baseName=$(basename "$srcDir")_$(date +%Y%m%d)
	mainName=$baseName
	if [ -r "${baseName}.7z" ]; then
		for((i=1; ; i++)) {
			mainName="${baseName}_$(printf "%04u" $i)"
			if [ ! -r "${mainName}.7z" ]; then
				break
			fi
		}
	fi

	tmpDir=~/~tmp-$mainName
	if [ "$1" != all ]; then
		case "$srcDir" in
		$MYDROID)    excludeList=$(make_exclude_list_mydroid);;
		$KERNELDIR)  excludeList=$(make_exclude_list_kernel);;
		esac
	fi
	echo "rsync -a $excludeList $srcDir $tmpDir"
	rsync -a $excludeList $srcDir $tmpDir
	if [ $? -eq 0 ]; then
		7za a -mmt=12 "${mainName}.7z" $tmpDir
	fi
	rm -rf $tmpDir/
}

pack_mydroid()
{
	pack_common "$MYDROID" "$1"
}

pack_mydroid
