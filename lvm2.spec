#
# Conditional build:
%bcond_without	initrd	# don't build initrd version
%bcond_without	uClibc	# link initrd version with static glibc instead of uClibc
%bcond_without	clvmd	# do not build clvmd
#
%ifarch amd64
%undefine	with_uClibc
%endif
Summary:	The new version of Logical Volume Manager for Linux
Summary(pl):	Nowa wersja Logical Volume Managera dla Linuksa
Name:		lvm2
Version:	2.00.32
Release:	1
License:	GPL
Group:		Applications/System
Source0:	ftp://sources.redhat.com/pub/lvm2/LVM2.%{version}.tgz
# Source0-md5:	66a6ad35f8e92aee6fe6cd6316972c04
%define	devmapper_ver	1.00.19
Source1:	ftp://sources.redhat.com/pub/dm/device-mapper.%{devmapper_ver}.tgz
# Source1-md5:	a7a97c469f22e3ec2cdcb5aae5603f3f
URL:		http://sources.redhat.com/lvm2/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	device-mapper-devel >= %{devmapper_ver}
BuildRequires:	libselinux-devel >= 1.10
%{?with_clvmd:BuildRequires:	dlm-devel}
%if %{with initrd}
%{!?with_uClibc:BuildRequires:	glibc-static}
%{?with_uClibc:BuildRequires:	uClibc-static >= 0.9.26}
%endif
Requires:	device-mapper
Requires:	libselinux >= 1.10
Obsoletes:	lvm
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin
%define		_libdir		/%{_lib}

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
%setup -q -n LVM2.%{version} -a1

%build
cp -f /usr/share/automake/config.sub autoconf
%{__aclocal}
%{__autoconf}

%if %{with initrd}
dm=$(ls -1d device-mapper*)
cd $dm
# no selinux for initrd
sed -i -e 's#AC_CHECK_LIB(selinux.*##g' configure.in
cp -f /usr/share/automake/config.sub autoconf
%{__aclocal}
%{__autoconf}
%configure \
        %{?with_uClibc:CC="%{_target_cpu}-uclibc-gcc"} \
	--with-optimisation="-Os" \
        --with-interface=ioctl \
	--disable-nls
unset CFLAGS || :
%{__make}
ar cru libdevmapper.a lib/ioctl/*.o lib/*.o
ranlib libdevmapper.a
cd ..
%{__aclocal}
%{__autoconf}
%configure \
	CFLAGS="-I$(pwd)/${dm}/include -DINITRD_WRAPPER=1" \
	%{?with_uClibc:CC="%{_target_cpu}-uclibc-gcc"} \
	--with-optimisation="-Os" \
	--enable-static_link \
	--with-lvm1=internal \
	--disable-selinux \
	--disable-nls
%{__make} \
	LDFLAGS+="-L$(pwd)/${dm} -L$(pwd)/lib"
mv -f tools/lvm.static initrd-lvm
%{__make} clean
rm -rf autom4te.cache config.cache
%endif

%{__aclocal}
%{__autoconf}
%configure \
	CFLAGS="%{rpmcflags}" \
	--enable-readline \
	--enable-fsadm \
	%{?with_clvmd:--with-clvmd} \
	--with-lvm1=internal \
	--with-pool=internal \
	--with-cluster=internal \
	--with-snapshots=internal \
	--with-mirrors=internal
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/lvm

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	OWNER="" \
	GROUP=""

touch $RPM_BUILD_ROOT%{_sysconfdir}/lvm/lvm.conf

%{?with_initrd:install initrd-lvm $RPM_BUILD_ROOT%{_sbindir}/initrd-lvm}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README WHATS_NEW doc/*
%attr(755,root,root) %{_sbindir}/*
%{?with_initrd:%exclude %{_sbindir}/initrd-lvm}
%{_mandir}/man?/*
%attr(750,root,root) %dir %{_sysconfdir}/lvm
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/lvm/lvm.conf

%if %{with initrd}
%files initrd
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/initrd-lvm
%endif
