# conditional build
#  --without initrd -- don't build initrd version

%ifnarch ppc %{ix86}
%define		_without_initrd	1
%endif

Summary:	Logical Volume Manager for Linux
Summary(pl):	Logical Volume Manager dla Linuksa
Name:		lvm2
Version:	1.0.7
Release:	1
License:	GPL
Group:		Applications/System
Source0:	ftp://ftp.sistina.com/pub/LVM/1.0/%{name}_%{version}.tar.gz
Patch0:		%{name}-BOOT.patch
Patch1:		%{name}-sparc.patch
Patch2:		%{name}-dietlibc.patch
Patch3:		%{name}-lvmtab_in_tmp.patch
URL:		http://www.sistina.com/products_lvm.htm
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	sh-utils
%{!?_without_initrd:BuildRequires:	dietlibc-static}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin
%define		_libdir		/lib

%description
This package includes a number of utilities for creating, checking,
and repairing logical volumes.

%description -l pl
Pakiet ten zawiera narzêdzia do tworzenia, sprawdzania i naprawiania
logicznych wolumenów dyskowych (LVM).

%package devel
Summary:	Header files and development documentation for %{name}
Summary(pl):	Pliki nag³ówkowe i dokumentacja do %{name}
Group:		Development/Libraries
Requires:	%{name} = %{version}

%description devel
Header files and development documentation for %{name}.

%description devel -l pl
Pliki nag³ówkowe i dokumentacja do %{name}.

%package static
Summary:        Static %{name} libraries 
Summary(pl):    Biblioteki statyczne %{name}
Group:          Development/Libraries
Requires:       %{name}-devel = %{version}

%description static
Static libraries for %{name}.

%description static -l pl
Biblioteki statyczne %{name}.

%package initrd
Summary:	Logical Volume Manager for Linux - initrd version
Summary(pl):	Logical Volume Manager dla Linuksa - wersja dla initrd
Group:		Base

%description initrd
This package includes a number of utilities for creating, checking,
and repairing logical volumes - staticaly linked for initrd.

%description -l pl initrd
Pakiet ten zawiera narzêdzia do tworzenia, sprawdzania i naprawiania
logicznych wolumenów dyskowych (LVM) - statycznie zlinkowane na 
potrzeby initrd.

%prep
%setup -q -n LVM/%{version}
%patch0 -p1
%ifarch sparc sparc64
%patch1 -p1
%endif
%patch2 -p1
%patch3 -p2

%build
%{__aclocal}
%{__autoconf}

%if %{?_without_initrd:0}%{!?_without_initrd:1}
cc="%{_target_cpu}-dietlibc-gcc"
%configure CC="$cc" 
%{__make} clean
%{__make} -C tools/lib liblvm-10.a
cd tools
for f in vgcreate lvcreate pvcreate vgscan vgchange ; do
	$cc -Ilib -I. %{rpmcflags} -Os -c -DJOINED -Dmain=${f}_main $f.c
done
$cc %{rpmcflags} -Os ../wrapper.c \
	vgcreate.o lvcreate.o pvcreate.o vgscan.o vgchange.o \
	-o ../wrapper lib/liblvm-10.a
%{__make} clean
cd ..
rm -f config.cache
unset cc
%endif

%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/lvmtab.d,%{_includedir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	OWNER=$(id -u) \
	GROUP=$(id -g)

install tools/lib/*.h	$RPM_BUILD_ROOT%{_includedir}

(cd $RPM_BUILD_ROOT%{_libdir}; ln -sf `ls lib*.so` liblvm.so)

%{!?_without_initrd:install wrapper $RPM_BUILD_ROOT%{_sbindir}/initrd-lvm}

%clean
rm -rf $RPM_BUILD_ROOT

%post -p %{_sbindir}/ldconfig
%postun -p %{_sbindir}/ldconfig

%files
%defattr(644,root,root,755)
%doc ABSTRACT CHANGELOG CONTRIBUTORS FAQ LVM-HOWTO README TODO WHATSNEW KNOWN_BUGS
%attr(755,root,root) %{_sbindir}/[elpv]*
%attr(755,root,root) %{_libdir}/lib*.so.*
%{_mandir}/man?/*
%attr(750,root,root) %{_sysconfdir}/lvmtab.d

%files devel
%defattr(644,root,root,755)
%{_includedir}/*.h
%attr(755,root,root) %{_libdir}%{_libdir}*.so

%files static
%attr(644,root,root) /usr%{_libdir}/*.a

%if %{?_without_initrd:0}%{!?_without_initrd:1}
%files initrd
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/initrd-lvm
%endif
