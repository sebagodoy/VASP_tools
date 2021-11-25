#### DOS definition
import matplotlib.pyplot as plt

print(' '*4+'> Loading DOS class')

#### Auxiliaty functions

class DOS:
    def __init__(self, Direction, Pol=True, Orb='spd', ml=False):
        # Direction: direction of DOSCAR file
        # Polarized: Boolean, polarized calc
        # Orb = 's', 'sp', 'spd', 'spdf'

        #### Check initial
        if Orb not in ['s', 'sp', 'spd', 'spdf']:
            quit('')


        #### Open, read Header
        with open(Direction) as f:
            DOSfile = f.readlines()

        self.NAtoms = int(DOSfile[0].split()[0])
        self.Fermi = float(DOSfile[5].split()[3])
        self.NDOS = int(DOSfile[5].split()[2])
        self.Name = DOSfile[4]

        #### Get Elist
        self.Elist = []
        for i in range(self.NDOS):
            self.Elist.append(float(DOSfile[6+i].split()[0]))

        #### DOS registry
        #   Item.DOS['who']['what']
        #   examples    Item.DOS['global']['+']     for global, spin +
        #               Item.DOS['1']['p+']         for atom 1, orbital p spin +
        #               Item.DOS['364']['d-']       for atom 364, orbital d spin -
        # Nomenclature allows construction of new DOS curves
        #   example     Item.DOS['1-23,+']['p']     for summing atoms 1 to 23, orbitals p + and -
        #               Item.DOS['23']['p']         for atom 23, spin + plus spin -
        #               Item.DOS['global']['+-']    for global, DOS spin + minus spin -

        #### Get Global
        self.DOS={}
        self.DOS['global'] = {'+':[],'-':[]}
        for i in range(self.NDOS):
            self.DOS['global']['+'].append(float(DOSfile[6+i].split()[1]))
            self.DOS['global']['-'].append(float(DOSfile[6 + i].split()[2]))

        #### Get by atom
        for iAt in range(self.NAtoms):
            StartIndex = 6+(self.NDOS+1)*(iAt+1)
            ## Configure slots
            self.DOS[str(iAt+1)]={}
            if Pol and Orb=='sp' and not ml:
                columnclass = {1: 's+', 2: 's-', 3: 'p+', 4: 'p-'}
            elif Pol and Orb=='spd' and not ml:
                columnclass = {1: 's+', 2: 's-', 3: 'p+', 4: 'p-', 5: 'd+', 6: 'd-'}
            elif Pol and Orb=='spdf' and not ml:
                columnclass = {1: 's+', 2: 's-', 3: 'p+', 4: 'p-', 5: 'd+', 6: 'd-',7:'f+',8:'f-'}

            ## Create slots
            for i in columnclass:
                self.DOS[str(iAt + 1)][columnclass[i]]=[]

            ## Retrieve DOS curves
            for k in range(self.NDOS):
                for Col in columnclass:
                    self.DOS[str(iAt+1)][columnclass[Col]].append(float(DOSfile[StartIndex+k].split()[Col]))



    #### Identification
    def __repr__(self):
        return 'DOS object: '+self.Name
    def __str__(self):
        return 'DOS object: '+self.Name


    #### Create New Curve by adding multiple curves
    def AddDOS(self, Index, ListIndex, **kwargs):
        # Creates a new DOS curve from the ones on the dicctionary
        # Index = ('Who', 'What)    tuple of string indexes for the new curve
        #                           New curve created can be accesed
        #                           as self.DOS['Who']['What']
        # ListIndex = [('Who 1','What 1'), ('Who 2','What 2'), ...]
        #                           List of index tuples for the curves
        #                           to combine

        #### Checks
        if not isinstance(Index,tuple):
            quit('Attempted to create new DOS curve. Second parameter must be tuple of strings')
        if not (isinstance(Index[0], str) or isinstance(Index[1], str)):
            quit('Attempted to create new DOS curve. Second parameter must be tuple of strings')
        ## Check if already exist
        if Index[0] in self.DOS:
            if Index[1] in self.DOS[Index[0]]:
                quit('Attempted to create new DOS curve. But there is already a curve for '+str(Index)+'.')
        ## Check the required curves exist
        try:
            for iTuple in ListIndex:
                print(iTuple)
                self.DOS[iTuple[0]][iTuple[1]]
        except:
            quit('Attempted to create new DOS curve. Third parameter must contain existing curves but some indexes (\'Who\',\'What\') are not recognized')


        #### Construct
        ## if Index[0] is not a defined dicctionary already
        if not Index[0] in self.DOS:
            self.DOS[Index[0]]={}
        ## Construct curve list
        self.DOS[Index[0]][Index[1]]=[]
        for i in range(self.NDOS):
            self.DOS[Index[0]][Index[1]].append(0.)
        ## Agregate acordingly
        for iDOS in range(self.NDOS):
            for Curve2Add in ListIndex:
                self.DOS[Index[0]][Index[1]][iDOS]+=self.DOS[Curve2Add[0]][Curve2Add[1]][iDOS]

        if kwargs.get('Report',False):
            print(' '*4+'> Created new sum curve indexed as '+str(Index)+' from DOS '+str(ListIndex))


    def AvrgDOS(self, Index, ListIndex, **kwargs):
        # Creates a new DOS curve from the ones on the dicctionary
        # Index = ('Who', 'What)    tuple of string indexes for the new curve
        #                           New curve created can be accesed
        #                           as self.DOS['Who']['What']
        # ListIndex = [('Who 1','What 1'), ('Who 2','What 2'), ...]
        #                           List of index tuples for the curves
        #                           to average

        # first add
        self.AddDOS(Index, ListIndex)
        # Now average
        for i in range(self.NDOS):
            self.DOS[Index[0]][Index[1]][i]*=1./len(ListIndex)

        ## Report
        if kwargs.get('Report', False):
            print(' '*4+'> Created new average curve indexed as '+str(Index)+' from DOS '+str(ListIndex))


    def DiffDOS(self, Index, DOSplus, DOSminus, **kwargs):
        # Creates a new DOS curve from two on the dicctionary
        # Index = ('Who', 'What)    tuple of string indexes for the new curve
        #                           New curve created can be accesed
        #                           as self.DOS['Who']['What']
        # ListIndex = [('Who 1','What 1'), ('Who 2','What 2'), ...]
        #                           List of index tuples for the curves
        #                           to combine

        #### Checks
        if not isinstance(Index,tuple):
            quit('Attempted to create new DOS curve. Second parameter must be tuple of strings')
        if not (isinstance(Index[0], str) or isinstance(Index[1], str)):
            quit('Attempted to create new DOS curve. Second parameter must be tuple of strings')
        ## Check if already exist
        if Index[0] in self.DOS:
            if Index[1] in self.DOS[Index[0]]:
                quit('Attempted to create new DOS curve. But there is already a curve for '+str(Index)+'.')
        ## Check the required curves exist
        try:
            self.DOS[DOSplus[0]][DOSplus[1]]
            self.DOS[DOSminus[0]][DOSminus[1]]
        except:
            quit('Attempted to create new DOS curve. Second and third parameters must contain existing curves but some indexes (\'Who\',\'What\') are not recognized')


        #### Construct
        ## if Index[0] is not a defined dicctionary already
        if not Index[0] in self.DOS:
            self.DOS[Index[0]]={}
        ## Construct curve list
        self.DOS[Index[0]][Index[1]]=[]
        for i in range(self.NDOS):
            self.DOS[Index[0]][Index[1]].append(self.DOS[DOSplus[0]][DOSplus[1]][i]-self.DOS[DOSminus[0]][DOSminus[1]][i])


        ## Report
        if kwargs.get('Report', False):
            print(' '*4+'> Created new difference curve of index  '+str(Index)+' from '+str(DOSplus)+' - '+str(DOSminus))


    def BandCenter(self, Index, FilledLevels=True, FermiCorrected=True, **kwargs):
        ####    Compute the weigthed band center of the
        #       band self.DOS[Index[0]][Index[1]]
        # Options:  FilledLevels = False        to include levels above fermi level
        #           FermiCorrected = False      to avoid correction to the fermi level

        #### Checks
        try:
            self.DOS[Index[0]][Index[1]]
        except:
            quit(' '*4+'> Attempted to compute weighted band center but failed. Requested band '+str(Index)+' does not exist in '+print(self))

        #### Set Upper limit
        ELimit = self.Fermi
        if not FilledLevels:
            ELimit = self.Elist[-1]+1.

        #### Compute
        BandCenter=0.
        for i in range(self.NDOS):
            if self.Elist[i]<= ELimit:
                BandCenter+=self.DOS[Index[0]][Index[1]][i]*self.Elist[i]
        BandCenter *=1/sum(self.DOS[Index[0]][Index[1]])

        #### Fermi correct
        if FermiCorrected:
            BandCenter-=self.Fermi

        #### Report
        if not kwargs.get('Report', True):
            print(' '*4+'> Computed weighted band center for '+str(Index), end='')
            if FermiCorrected: print(', corrected to fermi level', end='')
            if not FilledLevels: print(', including empty levels', end='')
            print(' : '+str(BandCenter))

        #### Return value
        return BandCenter

    # TODO: add integrate function

    def Plot(self, Index, **kwargs):
        #### Add DOS curve from Index to active plot

        FermiCorrected = kwargs.get('FermiCorrected', True)
        PlotDown = kwargs.get('PlotDown', False)
        AmplifyFactor = kwargs.get('AmplifyFactor', 1.)

        LineWidth = kwargs.get('LineWidth', 1.5)
        LineAlpha = kwargs.get('AlphaLine', .3)
        LineStyle = kwargs.get('LineStyle', 'solid')
        Color = kwargs.get('Color', 'k')
        Filled = kwargs.get('Filled', True)
        AlphaFill = kwargs.get('AlphaFill', .1)
        ColorFill = kwargs.get('ColorFill', Color)

        #### Prepare correction and factor
        if FermiCorrected: Corr = self.Fermi
        else: Corr = 0.
        if PlotDown: Fact = -AmplifyFactor
        else: Fact = AmplifyFactor

        #### Plot
        plt.plot([i-Corr for i in self.Elist], [k*Fact for k in self.DOS[Index[0]][Index[1]]],
                 color=Color, linestyle=LineStyle, linewidth=LineWidth, alpha=LineAlpha)

        if Filled:
            plt.fill_between([i - Corr for i in self.Elist], 0, [k * Fact for k in self.DOS[Index[0]][Index[1]]],
                             alpha=AlphaFill, color=ColorFill)


