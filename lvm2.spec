#
# Conditional build:
%bcond_without	initrd	# don't build initrd version
#
#%ifnarch ppc %{ix86}
%undefine	with_initrd
#%endif
Summary:	The new version of Logical Volume Manager for Linux
Summary(pl):	Nowa wersja Logical Volume Managera dla Linuksa
Name:		lvm2
Version:	2.00.08
Release:	0.1
License:	GPL
Group:		Applications/System
Source0:	ftp://ftp.sistina.com/pub/LVM2/tools/LVM2.%{version}.tgz
# Source0-md5:	ed973eda318f3685ad317afb9a54c571
Patch0:		%{name}-DESTDIR.patch
Patch1:		%{name}-opt.patch
URL:		http://www.sistina.com/products_lvm.htm
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	device-mapper-devel >= 1.00.07
%{?with_initrd:BuildRequires:	dietlibc-static}
Requires:	device-mapper
Obsoletes:	lvm
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin
%define		_libdir		/lib

%description
This package includes a number of utilities for creating, checking,
and repairing logical volumes.

%description -l pl
Pakiet ten zawiera narzêdzia do tworzenia, sprawdzania i naprawiania
logicznych wolumenów dyskowych (LVM2).

%package initrd
Summary:	The new version of Logical Volume Manager for Linux - initrd version
Summary(pl):	Nowa wersja Logical Volume Managera dla Linuksa - wersja dla initrd
Group:		Base

%description initrd
This package includes a number of utilities for creating, checking,
and repairing logical volumes - staticaly linked for initrd.

%description initrd -l pl
Pakiet ten zawiera narzêdzia do tworzenia, sprawdzania i naprawiania
logicznych wolumenów dyskowych (LVM2) - statycznie skonsolidowane na
potrzeby initrd.

%prep
%setup -q -n LVM2.%{version}
%patch0 -p1
%patch1 -p1

%build
%{__aclocal}
%{__autoconf}

%if %{with initrd}
cc="%{_target_cpu}-dietlibc-gcc"
%configure \
	CC="$cc"
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

%configure \
	--with-lvm1=internal
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/lvm

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	OWNER=$(id -u) \
	GROUP=$(id -g)

touch $RPM_BUILD_ROOT%{_sysconfdir}/lvm/lvm.conf

%{?with_initrd:install wrapper $RPM_BUILD_ROOT%{_sbindir}/initrd-lvm}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README WHATS_NEW doc/*
%attr(755,root,root) %{_sbindir}/[elpv]*
%{_mandir}/man?/*
%attr(750,root,root) %dir %{_sysconfdir}/lvm
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/lvm/lvm.conf

%if %{with initrd}
%files initrd
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/initrd-lvm
%endif
