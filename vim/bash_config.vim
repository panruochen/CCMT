
function! RunMake(names, ...)
	for x in a:names
		let makefile = findfile(l:x, ".;")
		if !empty(makefile) && filereadable(makefile)
			let d = tr(fnamemodify(makefile, ":p:h"), "\\", "/")
			let f = fnamemodify(makefile, ":t")
			let cl = ":make -C " . d . " -f " . f
			for i in a:000
				let cl = cl . ' '  . i
			endfor
"			echo cl
			exec cl
		endif
	endfor
endfunction

let s:MSYS_BASH  = 'C:/MinGW/msys/1.0/bin/bash.exe'
"let s:MSYS_MAKE  = 'mingw32-make'

let $BASH_ENV = expand('<sfile>:p:h') . '/bashenv'

let &shell=s:MSYS_BASH
set shellcmdflag=-c
set shellslash
set shellxquote=\"
set shellpipe=2>&1\|tee
"let &makeprg = s:MSYS_MAKE

"noremap <F7> :call RunMake(['Makefile', 'GNUmakefile'])<CR>
command -nargs=* Qmake  call RunMake(['Makefile', 'GNUmakefile'],<f-args>)
