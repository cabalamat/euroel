# dhondt.py = calculate d'Hondt

#---------------------------------------------------------------------

def greatestRemainder(votes, totSeats):
    """ Apportion seats using greatest remainder. Interface like
    dhondt().
    Allocates seats by whole d'Hondt quotas then greatest remainders.

    @param votes [list of num]
    @param totSeats [int]
    @return [list of int]
    """
    totVotes = sum(votes)
    quota = int(totVotes/(totSeats+1)) + 1
    quotas = [v*1.0/quota for v in votes]
    wholeQuotas = [int(q) for q in quotas]
    remainders = [q-int(q) for q in quotas]
    remainingSeats = totSeats - sum(wholeQuotas)
    remaindersWithIndexes = list(enumerate(remainders))
    #print "remaindersWithIndexes=%r" % (remaindersWithIndexes,)
    remaindersWithIndexes.sort(
        lambda x, y: cmp(x[1], y[1]),
        reverse = True)
    #print "remaindersWithIndexes=%r" % (remaindersWithIndexes,)
    result = wholeQuotas
    for ix,_ in remaindersWithIndexes[:remainingSeats]:
        result[ix] += 1
    #print "greatestRemainder() => %r" % (result,)
    return result


#---------------------------------------------------------------------



def dhondtDivisorFn(votes, allocSeats):
    divisors = [v*1.0/(s+1)
                for v, s in zip(votes, allocSeats)]
    return divisors

def sainteLagueDivisorFn(votes, allocSeats):
    divisors = [v*1.0/(s+0.5)
                for v, s in zip(votes, allocSeats)]
    return divisors

def dhondt(votes, totSeats):
    """ Run a dhondt election
    @param votes [list of num]
    @param totSeats [int]
    @return [list of int]
    """
    #print ("@@@@@ dhondt votes=%r totSeats=%r"
    #       % (votes, totSeats))
    return dhondtIter(votes, [0 for v in votes], totSeats)

def sainteLague(votes, totSeats):
    """ Run a dhondt election
    @param votes [list of num]
    @param totSeats [int]
    @return [list of int]
    """
    return dhondtIter(votes,
                      [0 for v in votes],
                      totSeats,
                      sainteLagueDivisorFn)

def dhondtIter(votes, allocSeats, unallocSeats, divisorFn=dhondtDivisorFn):
    """ Run a dhondt election
    @param votes [list of num]
    @param allocSeats [list of int]
    @param unallocSeats [int]
    @param divisorFn [function] function used to calculate divisors
    @return [list of int]
    """
    #print ("@@@@@ dhondtIter votes=%r allocSeats=%r unallocSeats=%r"
    #       % (votes, allocSeats, unallocSeats))
    while unallocSeats > 0:
        divisors = divisorFn(votes, allocSeats)
        bigDivIx = biggestIndex(divisors)
        allocSeats[bigDivIx] += 1
        unallocSeats -= 1
    #//while
    return allocSeats

def biggestIndex(ar):
    """ Return the index in ar with the greatest value
    @param ar [list]
    @return [int]
    """
    for ix,el in enumerate(ar):
        if ix==0:
            bestIx = ix; best = el
        else:
            if el>best:
                bestIx = ix; best = el
    #//for
    return bestIx


def getSeats(partyVotes, totSeats):
    """ get the number of seats of each party
    @partyVotes [dict(str, int)] votes for each party
    @param totSeats [int] totla number of seats
    @return [dict(str, int)] e.g. {'snp':2, 'lab':1,..}
    """
    pv = partyVotes.items()
    votes = map(None, *pv)[1] # just the votes
    seats = dhondt(votes, totSeats)
    #seats = sainteLague(votes, totSeats)
    #seats = greatestRemainder(votes, totSeats)
    result = {}
    for ix in range(len(pv)):
        result[pv[ix][0]] = seats[ix]
    return result



#end